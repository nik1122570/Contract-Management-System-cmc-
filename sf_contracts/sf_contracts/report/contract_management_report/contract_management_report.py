import frappe
from frappe import _
from frappe.utils import add_days, date_diff, flt, getdate, nowdate


LIFECYCLE_STATUSES = (
	"Active",
	"Expired",
	"Terminated",
)


def execute(filters=None):
	filters = frappe._dict(filters or {})
	contracts = get_contracts(filters)

	if filters.get("report_view") == "Summary List":
		columns = get_summary_columns()
		data = get_summary_data(contracts)
	else:
		columns = get_detail_columns()
		data = get_detail_data(contracts)

	return columns, data, None, get_chart(contracts), get_report_summary(contracts)


def get_contracts(filters):
	conditions = []
	values = {}
	company_field = get_contract_company_field()

	if filters.get("lifecycle_status"):
		conditions.append("c.sf_contract_lifecycle_status = %(lifecycle_status)s")
		values["lifecycle_status"] = filters.lifecycle_status

	if filters.get("health_score"):
		conditions.append("c.sf_contract_health_score = %(health_score)s")
		values["health_score"] = filters.health_score

	if filters.get("party_type"):
		conditions.append("c.party_type = %(party_type)s")
		values["party_type"] = filters.party_type

	if filters.get("party_name"):
		conditions.append("c.party_name like %(party_name)s")
		values["party_name"] = f"%{filters.party_name}%"

	if filters.get("company") and company_field:
		conditions.append(f"c.`{company_field}` = %(company)s")
		values["company"] = filters.company
	elif filters.get("company"):
		conditions.append("1 = 0")

	if filters.get("contractor"):
		conditions.append("c.sf_contractor = %(contractor)s")
		values["contractor"] = filters.contractor

	if filters.get("contract_type"):
		conditions.append("c.sf_contract_type = %(contract_type)s")
		values["contract_type"] = filters.contract_type

	if filters.get("from_date"):
		conditions.append("c.start_date >= %(from_date)s")
		values["from_date"] = filters.from_date

	if filters.get("to_date"):
		conditions.append("c.end_date <= %(to_date)s")
		values["to_date"] = filters.to_date

	if filters.get("expiry_within_days"):
		conditions.append("c.end_date between %(today)s and %(expiry_limit)s")
		values["today"] = nowdate()
		values["expiry_limit"] = add_days(nowdate(), filters.expiry_within_days)

	where_clause = " where " + " and ".join(conditions) if conditions else ""
	company_select = f"c.`{company_field}` as company" if company_field else "'' as company"

	return frappe.db.sql(
		f"""
		select
			c.name,
			{company_select},
			c.party_type,
			c.party_name,
			c.sf_contractor,
			c.sf_contract_type,
			c.sf_contract_lifecycle_status,
			c.sf_contract_health_score,
			c.sf_contract_health_reason,
			c.start_date,
			c.end_date,
			c.sf_signed_contract_document,
			(
				select tracker.name
				from `tabContract Compliance Tracker` tracker
				where tracker.contract = c.name
				order by tracker.evaluation_date desc, tracker.creation desc
				limit 1
			) as sf_compliance_tracker,
			(
				select tracker.compliance_percentage
				from `tabContract Compliance Tracker` tracker
				where tracker.contract = c.name
				order by tracker.evaluation_date desc, tracker.creation desc
				limit 1
			) as compliance_percentage
		from `tabContract` c
		{where_clause}
		order by
			field(c.sf_contract_lifecycle_status, 'Active', 'Expired', 'Terminated'),
			c.end_date asc,
			c.modified desc
		""",
		values,
		as_dict=True,
	)


def get_contract_company_field():
	"""Return the Contract field used for SF company/entity, if available.

	Some sites have a manually-created Link field labelled Company, for example
	`link_abmz`, instead of a database column named `company`.
	"""
	if frappe.db.has_column("Contract", "company"):
		return "company"

	meta = frappe.get_meta("Contract")
	for df in meta.fields:
		if (
			df.fieldtype == "Link"
			and df.options == "SF Companies"
			and (df.label or "").strip().lower() in {"company", "sf company", "entity", "entity / company"}
			and frappe.db.has_column("Contract", df.fieldname)
		):
			return df.fieldname

	return None


def get_detail_columns():
	return [
		{"label": _("Contract"), "fieldname": "name", "fieldtype": "Link", "options": "Contract", "width": 180},
		{"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "SF Companies", "width": 190},
		{"label": _("Party"), "fieldname": "party_name", "fieldtype": "Data", "width": 180},
		{"label": _("Contractor"), "fieldname": "sf_contractor", "fieldtype": "Link", "options": "Contractor", "width": 160},
		{"label": _("Contract Type"), "fieldname": "sf_contract_type", "fieldtype": "Link", "options": "Contract Type", "width": 150},
		{"label": _("Lifecycle Status"), "fieldname": "sf_contract_lifecycle_status", "fieldtype": "Data", "width": 170},
		{"label": _("Health"), "fieldname": "sf_contract_health_score", "fieldtype": "Data", "width": 130},
		{"label": _("Health Reason"), "fieldname": "sf_contract_health_reason", "fieldtype": "Data", "width": 240},
		{"label": _("Start Date"), "fieldname": "start_date", "fieldtype": "Date", "width": 110},
		{"label": _("End Date"), "fieldname": "end_date", "fieldtype": "Date", "width": 110},
		{"label": _("Days to Expiry"), "fieldname": "days_to_expiry", "fieldtype": "Int", "width": 120},
		{"label": _("Signed Document"), "fieldname": "sf_signed_contract_document", "fieldtype": "Data", "width": 220},
		{"label": _("Compliance %"), "fieldname": "compliance_percentage", "fieldtype": "Percent", "width": 120},
		{"label": _("Compliance Tracker"), "fieldname": "sf_compliance_tracker", "fieldtype": "Link", "options": "Contract Compliance Tracker", "width": 180},
	]


def get_detail_data(contracts):
	today = getdate(nowdate())
	data = []

	for contract in contracts:
		end_date = getdate(contract.end_date) if contract.end_date else None
		data.append(
			{
				**contract,
				"days_to_expiry": date_diff(end_date, today) if end_date else None,
				"compliance_percentage": flt(contract.compliance_percentage) if contract.compliance_percentage is not None else None,
			}
		)

	return data


def get_summary_columns():
	return [
		{"label": _("Lifecycle Status"), "fieldname": "lifecycle_status", "fieldtype": "Data", "width": 190},
		{"label": _("Total Contracts"), "fieldname": "total_contracts", "fieldtype": "Int", "width": 130},
		{"label": _("Critical"), "fieldname": "critical_contracts", "fieldtype": "Int", "width": 100},
		{"label": _("Attention Needed"), "fieldname": "attention_needed_contracts", "fieldtype": "Int", "width": 140},
		{"label": _("Healthy"), "fieldname": "healthy_contracts", "fieldtype": "Int", "width": 100},
		{"label": _("Average Compliance %"), "fieldname": "average_compliance", "fieldtype": "Percent", "width": 150},
	]


def get_summary_data(contracts):
	summary = {status: new_summary_row(status) for status in LIFECYCLE_STATUSES}

	for contract in contracts:
		status = contract.sf_contract_lifecycle_status or "Active"
		summary.setdefault(status, new_summary_row(status))
		row = summary[status]
		row["total_contracts"] += 1

		health = contract.sf_contract_health_score
		if health == "Critical":
			row["critical_contracts"] += 1
		elif health == "Attention Needed":
			row["attention_needed_contracts"] += 1
		elif health == "Healthy":
			row["healthy_contracts"] += 1

		if contract.compliance_percentage is not None:
			row["_compliance_total"] += flt(contract.compliance_percentage)
			row["_compliance_count"] += 1

	for row in summary.values():
		if row["_compliance_count"]:
			row["average_compliance"] = row["_compliance_total"] / row["_compliance_count"]
		row.pop("_compliance_total")
		row.pop("_compliance_count")

	return list(summary.values())


def new_summary_row(status):
	return {
		"lifecycle_status": status,
		"total_contracts": 0,
		"critical_contracts": 0,
		"attention_needed_contracts": 0,
		"healthy_contracts": 0,
		"average_compliance": None,
		"_compliance_total": 0,
		"_compliance_count": 0,
	}


def get_chart(contracts):
	counts = {status: 0 for status in LIFECYCLE_STATUSES}
	for contract in contracts:
		counts[contract.sf_contract_lifecycle_status or "Active"] = counts.get(
			contract.sf_contract_lifecycle_status or "Active", 0
		) + 1

	return {
		"data": {
			"labels": list(counts.keys()),
			"datasets": [{"name": _("Contracts"), "values": list(counts.values())}],
		},
		"type": "donut",
	}


def get_report_summary(contracts):
	total = len(contracts)
	critical = sum(1 for contract in contracts if contract.sf_contract_health_score == "Critical")
	attention = sum(1 for contract in contracts if contract.sf_contract_health_score == "Attention Needed")
	healthy = sum(1 for contract in contracts if contract.sf_contract_health_score == "Healthy")

	return [
		{"label": _("Total Contracts"), "value": total, "indicator": "Blue"},
		{"label": _("Critical"), "value": critical, "indicator": "Red"},
		{"label": _("Attention Needed"), "value": attention, "indicator": "Orange"},
		{"label": _("Healthy"), "value": healthy, "indicator": "Green"},
	]
