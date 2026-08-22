import frappe
from frappe import _
from frappe.utils import date_diff, getdate, nowdate


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = get_columns()
	data = get_data(filters)
	return columns, data, None, None, get_summary(data)


def get_columns():
	return [
		{"label": _("Overdue Stage"), "fieldname": "overdue_stage", "fieldtype": "Data", "width": 130},
		{"label": _("Days Overdue"), "fieldname": "days_overdue", "fieldtype": "Int", "width": 110},
		{"label": _("Period"), "fieldname": "period_key", "fieldtype": "Data", "width": 100},
		{"label": _("Employee"), "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 130},
		{"label": _("Employee Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 180},
		{"label": _("Company"), "fieldname": "company", "fieldtype": "Link", "options": "Company", "width": 180},
		{"label": _("Department"), "fieldname": "department", "fieldtype": "Link", "options": "Department", "width": 160},
		{"label": _("Workflow Status"), "fieldname": "workflow_status", "fieldtype": "Data", "width": 160},
		{"label": _("Due Date"), "fieldname": "due_date", "fieldtype": "Date", "width": 110},
		{"label": _("KPI Review"), "fieldname": "name", "fieldtype": "Link", "options": "KPI Review", "width": 150},
	]


def get_data(filters):
	conditions = ["docstatus != 2", "workflow_status in ('Pending Self Rating', 'Pending Final Rating')"]
	values = {"today": nowdate()}

	if filters.get("company"):
		conditions.append("company = %(company)s")
		values["company"] = filters.company
	if filters.get("department"):
		conditions.append("department = %(department)s")
		values["department"] = filters.department

	rows = frappe.db.sql(
		f"""
		select
			name,
			period_key,
			employee,
			employee_name,
			company,
			department,
			workflow_status,
			self_rating_due_date,
			final_rating_due_date
		from `tabKPI Review`
		where {" and ".join(conditions)}
		order by self_rating_due_date asc, final_rating_due_date asc
		""",
		values,
		as_dict=True,
	)

	today_date = getdate(nowdate())
	data = []
	for row in rows:
		if row.workflow_status == "Pending Self Rating":
			stage = "Self Rating"
			due_date = row.self_rating_due_date
		else:
			stage = "Final Rating"
			due_date = row.final_rating_due_date

		if filters.get("overdue_stage") and filters.overdue_stage != stage:
			continue
		if not due_date or getdate(due_date) >= today_date:
			continue

		row.overdue_stage = stage
		row.due_date = due_date
		row.days_overdue = date_diff(today_date, getdate(due_date))
		data.append(row)

	return data


def get_summary(data):
	return [
		{"label": _("Overdue Reviews"), "value": len(data), "indicator": "Red", "datatype": "Int"},
	]
