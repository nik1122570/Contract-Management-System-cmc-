import json

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import flt


class KPIStructure(Document):
	def autoname(self):
		if self.name:
			return
		prefix = frappe.scrub(self.designation or "KPI").replace("_", "-").upper()
		self.name = make_autoname(f"{prefix}-KPI-.####")

	def validate(self):
		self.set_structure_items()
		self.set_total_weight()
		self.validate_duplicate_components()
		if self.status == "Active":
			self.validate_total_weight()

	def before_submit(self):
		self.status = "Active"
		self.validate_total_weight()

	def on_submit(self):
		self.supersede_previous_versions()

	def set_structure_items(self):
		for row in self.components:
			if not row.kpi_component:
				continue
			component = frappe.db.get_value(
				"KPI Component",
				row.kpi_component,
				[
					"objective",
					"perspective",
					"metric",
					"indicator",
					"scoring_method",
					"evidence_required",
					"default_target_operator",
					"default_target_value",
					"default_target_value_2",
					"status",
				],
				as_dict=True,
			)
			if not component:
				continue
			if component.status != "Active":
				frappe.throw(_("Row {0}: KPI Component must be Active.").format(row.idx))
			row.objective = component.objective
			row.perspective = row.perspective or component.perspective
			row.metric = component.metric
			row.indicator = component.indicator
			row.scoring_method = row.scoring_method or component.scoring_method
			row.evidence_required = row.evidence_required or component.evidence_required
			row.target_operator = row.target_operator or component.default_target_operator
			row.target_value = row.target_value if row.target_value is not None else component.default_target_value
			row.target_value_2 = row.target_value_2 if row.target_value_2 is not None else component.default_target_value_2
			row.target_display = get_target_display(row.target_operator, row.target_value, row.target_value_2)

	def set_total_weight(self):
		self.total_weight = sum(flt(row.weight) for row in self.components)

	def validate_duplicate_components(self):
		seen = set()
		for row in self.components:
			if row.kpi_component in seen:
				frappe.throw(_("KPI Component {0} appears more than once.").format(row.kpi_component))
			seen.add(row.kpi_component)
			if flt(row.weight) <= 0:
				frappe.throw(_("Row {0}: Weight must be greater than zero.").format(row.idx))

	def validate_total_weight(self):
		if flt(self.total_weight, 2) != 100:
			frappe.throw(_("Total Weight must equal exactly 100 before activation/submission. Current total is {0}.").format(self.total_weight))

	def supersede_previous_versions(self):
		filters = {
			"designation": self.designation,
			"status": "Active",
			"docstatus": 1,
			"name": ["!=", self.name],
		}
		if self.company:
			filters["company"] = self.company
		else:
			filters["company"] = ["is", "not set"]

		for previous in frappe.get_all("KPI Structure", filters=filters, pluck="name"):
			frappe.db.set_value(
				"KPI Structure",
				previous,
				{"status": "Superseded", "effective_to": self.effective_from},
				update_modified=False,
			)


def get_target_display(operator, value, value_2=None):
	if not operator:
		return ""
	if operator == "Range":
		return f"{value or 0} - {value_2 or 0}"
	return f"{operator} {value or 0}"


@frappe.whitelist()
def bulk_assign_kpi_structure(
	kpi_structure,
	employees,
	start_date,
	end_date,
	review_frequency,
	self_rating_due_days=7,
	final_rating_due_days=7,
	submit_assignments=1,
):
	if not has_any_role("System Manager", "KPI Manager"):
		frappe.throw(_("Only System Manager or KPI Manager can assign KPI Structures in bulk."))

	if isinstance(employees, str):
		employees = json.loads(employees)

	employee_names = []
	for row in employees or []:
		if isinstance(row, dict):
			employee = row.get("employee")
		else:
			employee = row
		if employee and employee not in employee_names:
			employee_names.append(employee)

	if not employee_names:
		frappe.throw(_("Please select at least one Employee."))

	structure = frappe.db.get_value(
		"KPI Structure",
		kpi_structure,
		["name", "designation", "company", "status", "docstatus", "effective_from", "effective_to"],
		as_dict=True,
	)
	if not structure:
		frappe.throw(_("KPI Structure not found."))
	if structure.docstatus != 1 or structure.status != "Active":
		frappe.throw(_("KPI Structure must be submitted and Active before bulk assignment."))

	results = {"created": [], "skipped": [], "failed": []}

	for employee in employee_names:
		try:
			existing = get_overlapping_assignment(employee, start_date, end_date)
			if existing:
				results["skipped"].append(
					{
						"employee": employee,
						"reason": _("Overlapping Active assignment already exists: {0}").format(existing),
					}
				)
				continue

			assignment = frappe.new_doc("KPI Structure Assignment")
			assignment.employee = employee
			assignment.kpi_structure = kpi_structure
			assignment.start_date = start_date
			assignment.end_date = end_date
			assignment.review_frequency = review_frequency
			assignment.self_rating_due_days = self_rating_due_days or 7
			assignment.final_rating_due_days = final_rating_due_days or 7
			assignment.insert(ignore_permissions=True)

			if int(submit_assignments or 0):
				assignment.submit()

			results["created"].append({"employee": employee, "assignment": assignment.name})
		except Exception as exc:
			frappe.db.rollback()
			results["failed"].append({"employee": employee, "reason": str(exc)})
		else:
			frappe.db.commit()

	return results


def get_overlapping_assignment(employee, start_date, end_date):
	overlap = frappe.db.sql(
		"""
		select name
		from `tabKPI Structure Assignment`
		where employee = %(employee)s
			and docstatus = 1
			and status = 'Active'
			and start_date <= %(end_date)s
			and end_date >= %(start_date)s
		limit 1
		""",
		{
			"employee": employee,
			"start_date": start_date,
			"end_date": end_date,
		},
		as_dict=True,
	)
	return overlap[0].name if overlap else None


def has_any_role(*roles):
	user_roles = set(frappe.get_roles(frappe.session.user))
	return bool(user_roles.intersection(roles))
