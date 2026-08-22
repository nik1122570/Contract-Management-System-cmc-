import frappe
from frappe import _


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = get_columns()
	data = get_data(filters)
	return columns, data, None, get_chart(data)


def get_columns():
	return [
		{"label": _("Period"), "fieldname": "period_key", "fieldtype": "Data", "width": 100},
		{"label": _("Employee"), "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 130},
		{"label": _("Employee Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 180},
		{"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 180},
		{"label": _("Department"), "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 160},
		{"label": _("Designation"), "fieldname": "designation", "fieldtype": "Link", "options": "Designation", "width": 160},
		{"label": _("Workflow Status"), "fieldname": "workflow_status", "fieldtype": "Data", "width": 160},
		{"label": _("Self Total"), "fieldname": "self_total", "fieldtype": "Float", "width": 100},
		{"label": _("Final Total"), "fieldname": "final_total", "fieldtype": "Float", "width": 100},
		{"label": _("Rating Category"), "fieldname": "rating_category", "fieldtype": "Data", "width": 150},
		{"label": _("KPI Review"), "fieldname": "name", "fieldtype": "Link", "options": "KPI Review", "width": 150},
	]


def get_data(filters):
	conditions = ["docstatus != 2"]
	values = {}

	for field in ("company", "department", "designation", "period_key", "workflow_status"):
		if filters.get(field):
			conditions.append(f"{field} = %({field})s")
			values[field] = filters.get(field)

	return frappe.db.sql(
		f"""
		select
			name,
			period_key,
			employee,
			employee_name,
			company,
			department,
			designation,
			workflow_status,
			self_total,
			final_total,
			rating_category
		from `tabKPI Review`
		where {" and ".join(conditions)}
		order by period_end_date desc, company, department, employee_name
		""",
		values,
		as_dict=True,
	)


def get_chart(data):
	counts = {}
	for row in data:
		counts[row.workflow_status] = counts.get(row.workflow_status, 0) + 1
	return {
		"data": {"labels": list(counts), "datasets": [{"values": list(counts.values())}]},
		"type": "donut",
	}


