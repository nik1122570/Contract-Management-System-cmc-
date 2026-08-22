import calendar
from datetime import date

import frappe
from frappe import _
from frappe.utils import add_days, date_diff, getdate, now_datetime, today


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


def get_current_period(review_frequency, reference_date=None):
	reference = getdate(reference_date or today())
	year = reference.year
	month = reference.month

	if review_frequency == "Monthly":
		start, end = _month_bounds(year, month)
		return f"{year}-{month:02d}", start, end

	if review_frequency == "Quarterly":
		quarter = ((month - 1) // 3) + 1
		start_month = ((quarter - 1) * 3) + 1
		start, _ = _month_bounds(year, start_month)
		_, end = _month_bounds(year, start_month + 2)
		return f"{year}-Q{quarter}", start, end

	if review_frequency == "Semi-Annual":
		half = 1 if month <= 6 else 2
		start_month = 1 if half == 1 else 7
		start, _ = _month_bounds(year, start_month)
		_, end = _month_bounds(year, start_month + 5)
		return f"{year}-H{half}", start, end

	frappe.throw(_("Unsupported review frequency: {0}").format(review_frequency))


@frappe.whitelist()
def get_kpi_workspace_dashboard():
	today_date = getdate(today())
	assignments = frappe.get_all(
		"KPI Structure Assignment",
		filters={"docstatus": 1, "status": "Active"},
		fields=[
			"name",
			"employee",
			"employee_name",
			"review_frequency",
			"start_date",
			"end_date",
			"kpi_structure",
		],
	)

	next_events = []
	for assignment in assignments:
		if not assignment.review_frequency:
			continue
		period_key, period_start, period_end = get_current_period(assignment.review_frequency)
		if getdate(period_end) < getdate(assignment.start_date) or getdate(period_start) > getdate(assignment.end_date):
			continue
		next_date = getdate(add_days(period_end, 1))
		next_events.append(
			{
				"assignment": assignment.name,
				"employee": assignment.employee,
				"employee_name": assignment.employee_name,
				"kpi_structure": assignment.kpi_structure,
				"review_frequency": assignment.review_frequency,
				"period_key": period_key,
				"period_start_date": period_start,
				"period_end_date": period_end,
				"next_review_date": next_date,
				"days_to_next_review": date_diff(next_date, today_date),
			}
		)

	next_events = sorted(next_events, key=lambda row: row["next_review_date"])
	next_event_date = next_events[0]["next_review_date"] if next_events else None
	next_event_assignments = [
		row for row in next_events if row["next_review_date"] == next_event_date
	] if next_event_date else []

	return {
		"next_event": {
			"date": next_event_date,
			"days": date_diff(next_event_date, today_date) if next_event_date else None,
			"assignments": len(next_event_assignments),
			"periods": sorted({row["period_key"] for row in next_event_assignments}),
			"frequency": sorted({row["review_frequency"] for row in next_event_assignments}),
		},
		"counts": {
			"active_assignments": len(assignments),
			"pending_self_rating": frappe.db.count(
				"KPI Review",
				{"docstatus": ["!=", 2], "workflow_status": "Pending Self Rating"},
			),
			"pending_final_rating": frappe.db.count(
				"KPI Review",
				{"docstatus": ["!=", 2], "workflow_status": "Pending Final Rating"},
			),
			"completed_reviews": frappe.db.count(
				"KPI Review",
				{"docstatus": 1, "workflow_status": "Completed"},
			),
			"overdue_self_rating": frappe.db.count(
				"KPI Review",
				{
					"docstatus": ["!=", 2],
					"workflow_status": "Pending Self Rating",
					"self_rating_due_date": ["<", today_date],
				},
			),
			"overdue_final_rating": frappe.db.count(
				"KPI Review",
				{
					"docstatus": ["!=", 2],
					"workflow_status": "Pending Final Rating",
					"final_rating_due_date": ["<", today_date],
				},
			),
		},
		"upcoming": next_events[:5],
	}


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
