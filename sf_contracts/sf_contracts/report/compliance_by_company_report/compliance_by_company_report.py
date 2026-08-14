import frappe
from frappe import _
from frappe.utils import add_days, flt, nowdate


PRIORITY_ORDER = ("Critical", "High", "Medium", "Low")


def execute(filters=None):
	filters = frappe._dict(filters or {})
	rows = get_compliance_rows(filters)

	if filters.get("report_view") == "Summary List":
		columns = get_summary_columns()
		data = get_summary_data(rows)
	else:
		columns = get_detail_columns()
		data = rows

	return columns, data, None, get_chart(rows), get_report_summary(rows)


def get_compliance_rows(filters):
	conditions = []
	values = {}

	if filters.get("company"):
		conditions.append("company = %(company)s")
		values["company"] = filters.company

	if filters.get("party_name"):
		conditions.append("party_name like %(party_name)s")
		values["party_name"] = f"%{filters.party_name}%"

	if filters.get("compliance_category"):
		conditions.append("compliance_category = %(compliance_category)s")
		values["compliance_category"] = filters.compliance_category

	if filters.get("status"):
		conditions.append("status = %(status)s")
		values["status"] = filters.status

	if filters.get("priority"):
		conditions.append("priority = %(priority)s")
		values["priority"] = filters.priority

	if filters.get("due_from"):
		conditions.append("due_date >= %(due_from)s")
		values["due_from"] = filters.due_from

	if filters.get("due_to"):
		conditions.append("due_date <= %(due_to)s")
		values["due_to"] = filters.due_to

	if filters.get("expiry_from"):
		conditions.append("expiry_date >= %(expiry_from)s")
		values["expiry_from"] = filters.expiry_from

	if filters.get("expiry_to"):
		conditions.append("expiry_date <= %(expiry_to)s")
		values["expiry_to"] = filters.expiry_to

	if filters.get("expiry_within_days"):
		conditions.append("expiry_date between %(today)s and %(expiry_limit)s")
		values["today"] = nowdate()
		values["expiry_limit"] = add_days(nowdate(), filters.expiry_within_days)

	where_clause = " where " + " and ".join(conditions) if conditions else ""

	return frappe.db.sql(
		f"""
		select
			name,
			company,
			party_name,
			compliance_category,
			compliance_type,
			status,
			priority,
			authority,
			registration_or_license_no,
			due_date,
			expiry_date,
			days_to_expiry,
			amount,
			attachment,
			remarks
		from `tabCompliance Register`
		{where_clause}
		order by
			field(priority, 'Critical', 'High', 'Medium', 'Low'),
			days_to_expiry asc,
			expiry_date asc,
			modified desc
		""",
		values,
		as_dict=True,
	)


def get_detail_columns():
	return [
		{"label": _("Compliance Record"), "fieldname": "name", "fieldtype": "Link", "options": "Compliance Register", "width": 180},
		{"label": _("SF Company"), "fieldname": "company", "fieldtype": "Link", "options": "SF Companies", "width": 180},
		{"label": _("Entity / Company Name"), "fieldname": "party_name", "fieldtype": "Data", "width": 190},
		{"label": _("Compliance Category"), "fieldname": "compliance_category", "fieldtype": "Link", "options": "Compliance Category", "width": 180},
		{"label": _("Compliance Type"), "fieldname": "compliance_type", "fieldtype": "Data", "width": 160},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
		{"label": _("Priority"), "fieldname": "priority", "fieldtype": "Data", "width": 110},
		{"label": _("Authority"), "fieldname": "authority", "fieldtype": "Data", "width": 150},
		{"label": _("Registration / License No"), "fieldname": "registration_or_license_no", "fieldtype": "Data", "width": 180},
		{"label": _("Due Date"), "fieldname": "due_date", "fieldtype": "Date", "width": 110},
		{"label": _("Expiry / Renewal Date"), "fieldname": "expiry_date", "fieldtype": "Date", "width": 150},
		{"label": _("Days to Expiry"), "fieldname": "days_to_expiry", "fieldtype": "Int", "width": 120},
		{"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 130},
		{"label": _("Attachment"), "fieldname": "attachment", "fieldtype": "Data", "width": 180},
		{"label": _("Remarks"), "fieldname": "remarks", "fieldtype": "Data", "width": 220},
	]


def get_summary_columns():
	return [
		{"label": _("SF Company"), "fieldname": "company", "fieldtype": "Link", "options": "SF Companies", "width": 180},
		{"label": _("Compliance Category"), "fieldname": "compliance_category", "fieldtype": "Link", "options": "Compliance Category", "width": 190},
		{"label": _("Total Items"), "fieldname": "total_items", "fieldtype": "Int", "width": 110},
		{"label": _("Compliant"), "fieldname": "compliant", "fieldtype": "Int", "width": 100},
		{"label": _("Pending"), "fieldname": "pending", "fieldtype": "Int", "width": 100},
		{"label": _("Not Compliant"), "fieldname": "not_compliant", "fieldtype": "Int", "width": 120},
		{"label": _("Expired"), "fieldname": "expired", "fieldtype": "Int", "width": 100},
		{"label": _("Critical"), "fieldname": "critical", "fieldtype": "Int", "width": 100},
		{"label": _("High"), "fieldname": "high", "fieldtype": "Int", "width": 80},
		{"label": _("Medium"), "fieldname": "medium", "fieldtype": "Int", "width": 90},
		{"label": _("Low"), "fieldname": "low", "fieldtype": "Int", "width": 80},
		{"label": _("Compliance Rate"), "fieldname": "compliance_rate", "fieldtype": "Percent", "width": 130},
	]


def get_summary_data(rows):
	summary = {}

	for row in rows:
		key = (row.company or _("Not Set"), row.compliance_category or _("Not Set"))
		summary.setdefault(key, new_summary_row(*key))
		target = summary[key]
		target["total_items"] += 1

		status = row.status or ""
		if status in ("Compliant", "Paid", "Active", "Approved"):
			target["compliant"] += 1
		elif status in ("Pending", "In Progress", "N/A"):
			target["pending"] += 1
		elif status in ("Not Compliant", "Not Paid", "Not Approved"):
			target["not_compliant"] += 1
		elif status == "Expired":
			target["expired"] += 1
			target["not_compliant"] += 1

		if row.priority == "Critical":
			target["critical"] += 1
		elif row.priority == "High":
			target["high"] += 1
		elif row.priority == "Medium":
			target["medium"] += 1
		elif row.priority == "Low":
			target["low"] += 1

	for row in summary.values():
		if row["total_items"]:
			row["compliance_rate"] = flt(row["compliant"] / row["total_items"] * 100, 2)

	return list(summary.values())


def new_summary_row(company, compliance_category):
	return {
		"company": company,
		"compliance_category": compliance_category,
		"total_items": 0,
		"compliant": 0,
		"pending": 0,
		"not_compliant": 0,
		"expired": 0,
		"critical": 0,
		"high": 0,
		"medium": 0,
		"low": 0,
		"compliance_rate": 0,
	}


def get_chart(rows):
	counts = {priority: 0 for priority in PRIORITY_ORDER}
	for row in rows:
		if row.priority in counts:
			counts[row.priority] += 1

	return {
		"data": {
			"labels": list(counts.keys()),
			"datasets": [{"name": _("Compliance Items"), "values": list(counts.values())}],
		},
		"type": "donut",
	}


def get_report_summary(rows):
	total = len(rows)
	critical = sum(1 for row in rows if row.priority == "Critical")
	high = sum(1 for row in rows if row.priority == "High")
	expired = sum(1 for row in rows if row.status == "Expired" or flt(row.days_to_expiry) < 0)
	compliant = sum(1 for row in rows if row.status in ("Compliant", "Paid", "Active", "Approved"))

	return [
		{"label": _("Total Compliance Items"), "value": total, "indicator": "Blue"},
		{"label": _("Compliant Items"), "value": compliant, "indicator": "Green"},
		{"label": _("Critical Priority"), "value": critical, "indicator": "Red"},
		{"label": _("High Priority"), "value": high, "indicator": "Orange"},
		{"label": _("Expired"), "value": expired, "indicator": "Red"},
	]
