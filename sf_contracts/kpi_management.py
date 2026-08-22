import calendar
from datetime import date

import frappe
from frappe import _
from frappe.utils import add_days, getdate, now_datetime, today


def _month_bounds(year, month):
	start = date(year, month, 1)
	end = date(year, month, calendar.monthrange(year, month)[1])
	return start, end


def get_previous_closed_period(review_frequency, reference_date=None):
	reference = getdate(reference_date or today())
	year = reference.year
	month = reference.month

	if review_frequency == "Monthly":
		if month == 1:
			year -= 1
			month = 12
		else:
			month -= 1
		start, end = _month_bounds(year, month)
		return f"{year}-{month:02d}", start, end

	if review_frequency == "Quarterly":
		current_quarter = ((month - 1) // 3) + 1
		quarter = current_quarter - 1
		if quarter == 0:
			quarter = 4
			year -= 1
		start_month = ((quarter - 1) * 3) + 1
		start, _ = _month_bounds(year, start_month)
		_, end = _month_bounds(year, start_month + 2)
		return f"{year}-Q{quarter}", start, end

	if review_frequency == "Semi-Annual":
		if month <= 6:
			half = 2
			year -= 1
			start_month = 7
		else:
			half = 1
			start_month = 1
		start, _ = _month_bounds(year, start_month)
		_, end = _month_bounds(year, start_month + 5)
		return f"{year}-H{half}", start, end

	frappe.throw(_("Unsupported review frequency: {0}").format(review_frequency))


@frappe.whitelist()
def create_due_reviews(assignment=None, reference_date=None):
	assignments = _get_assignments(assignment)
	results = []

	for assignment_name in assignments:
		try:
			review = create_review_for_assignment(assignment_name, reference_date=reference_date)
			if review:
				results.append({"assignment": assignment_name, "status": "Created", "review": review})
			else:
				results.append({"assignment": assignment_name, "status": "Skipped"})
		except Exception:
			frappe.log_error(frappe.get_traceback(), _("KPI Review Scheduler Failed"))
			_log_scheduler(assignment_name, "", "Failed", None, frappe.get_traceback())
			results.append({"assignment": assignment_name, "status": "Failed"})

	return results


def _get_assignments(assignment=None):
	if assignment:
		return [assignment]
	return frappe.get_all(
		"KPI Structure Assignment",
		filters={"docstatus": 1, "status": "Active"},
		pluck="name",
	)


def create_review_for_assignment(assignment_name, reference_date=None):
	assignment = frappe.get_doc("KPI Structure Assignment", assignment_name)
	period_key, period_start, period_end = get_previous_closed_period(
		assignment.review_frequency,
		reference_date=reference_date,
	)

	if getdate(period_end) < getdate(assignment.start_date) or getdate(period_start) > getdate(assignment.end_date):
		_log_scheduler(assignment.name, period_key, "Skipped", None, "Period outside assignment validity.")
		return None

	existing = frappe.db.exists(
		"KPI Review",
		{
			"kpi_structure_assignment": assignment.name,
			"period_key": period_key,
			"docstatus": ["!=", 2],
		},
	)
	if existing:
		_log_scheduler(assignment.name, period_key, "Skipped", existing, "KPI Review already exists.")
		return None

	review = _build_review(assignment, period_key, period_start, period_end)
	review.insert(ignore_permissions=True)
	_log_scheduler(assignment.name, period_key, "Created", review.name, "KPI Review created.")
	return review.name


def _build_review(assignment, period_key, period_start, period_end):
	structure = frappe.get_doc("KPI Structure", assignment.kpi_structure)
	review = frappe.new_doc("KPI Review")
	review.employee = assignment.employee
	review.employee_name = assignment.employee_name
	review.employee_user = assignment.employee_user
	review.company = assignment.company
	review.department = assignment.department
	review.designation = assignment.designation
	review.kpi_structure_assignment = assignment.name
	review.kpi_structure = assignment.kpi_structure
	review.review_frequency = assignment.review_frequency
	review.period_key = period_key
	review.period_start_date = period_start
	review.period_end_date = period_end
	review.self_rating_due_date = add_days(period_end, assignment.self_rating_due_days or 7)
	review.final_rating_due_date = add_days(review.self_rating_due_date, assignment.final_rating_due_days or 7)
	review.workflow_status = "Pending Self Rating"

	overrides = {
		(row.kpi_component, row.period_key): row
		for row in assignment.target_overrides
		if row.kpi_component and row.period_key
	}

	for item in structure.components:
		override = overrides.get((item.kpi_component, period_key))
		target_operator = override.target_operator if override else item.target_operator
		target_value = override.target_value if override else item.target_value
		target_value_2 = override.target_value_2 if override else item.target_value_2
		review.append(
			"review_items",
			{
				"kpi_component": item.kpi_component,
				"objective": item.objective,
				"perspective": item.perspective,
				"metric": item.metric,
				"indicator": item.indicator,
				"target_operator": target_operator,
				"target_value": target_value,
				"target_value_2": target_value_2,
				"target_display": _get_target_display(target_operator, target_value, target_value_2),
				"weight": item.weight,
				"evidence_required": item.evidence_required,
			},
		)

	return review


def _get_target_display(operator, value, value_2=None):
	if not operator:
		return ""
	if operator == "Range":
		return f"{value or 0} - {value_2 or 0}"
	return f"{operator} {value or 0}"


def _log_scheduler(assignment, period_key, status, review, message):
	if not frappe.db.table_exists("KPI Scheduler Log"):
		return
	log = frappe.new_doc("KPI Scheduler Log")
	log.run_date = now_datetime()
	log.assignment = assignment
	log.period_key = period_key
	log.status = status
	log.kpi_review = review
	log.message = message[:1000] if message else ""
	log.insert(ignore_permissions=True)
