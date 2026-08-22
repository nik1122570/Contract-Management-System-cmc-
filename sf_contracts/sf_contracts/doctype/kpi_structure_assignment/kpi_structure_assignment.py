import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class KPIStructureAssignment(Document):
	def validate(self):
		self.sync_employee_and_structure_fields()
		self.validate_dates()
		if self.docstatus == 1 or self.status == "Active":
			self.validate_assignment_ready()
		self.validate_overlap()

	def before_submit(self):
		self.status = "Active"
		self.validate_assignment_ready()

	def on_cancel(self):
		self.status = "Cancelled"

	def sync_employee_and_structure_fields(self):
		if self.employee:
			employee = frappe.db.get_value(
				"Employee",
				self.employee,
				["employee_name", "company", "department", "designation", "user_id", "status"],
				as_dict=True,
			)
			if employee:
				self.employee_name = employee.employee_name
				self.company = employee.company
				self.department = employee.department
				self.designation = employee.designation
				self.employee_user = employee.user_id

		if self.kpi_structure:
			structure = frappe.db.get_value(
				"KPI Structure",
				self.kpi_structure,
				["designation", "company", "version", "effective_from", "effective_to", "status", "docstatus"],
				as_dict=True,
			)
			if structure:
				self.structure_designation = structure.designation
				self.structure_company = structure.company
				self.structure_version = structure.version

	def validate_dates(self):
		if self.start_date and self.end_date and getdate(self.start_date) > getdate(self.end_date):
			frappe.throw(_("Start Date cannot be after End Date."))

	def validate_assignment_ready(self):
		employee = frappe.db.get_value("Employee", self.employee, ["status"], as_dict=True)
		if not employee:
			frappe.throw(_("Employee is required."))
		if employee.status != "Active":
			frappe.throw(_("Employee must be Active before KPI assignment submission."))

		structure = frappe.db.get_value(
			"KPI Structure",
			self.kpi_structure,
			["designation", "company", "effective_from", "effective_to", "status", "docstatus"],
			as_dict=True,
		)
		if not structure or structure.docstatus != 1 or structure.status != "Active":
			frappe.throw(_("KPI Structure must be submitted and Active."))
		if self.designation != structure.designation:
			frappe.throw(_("Employee designation must match KPI Structure designation."))
		if structure.company and self.company != structure.company:
			frappe.throw(_("Employee company must match the company-specific KPI Structure."))
		if getdate(self.start_date) < getdate(structure.effective_from):
			frappe.throw(_("Assignment Start Date cannot be before Structure Effective From."))
		if structure.effective_to and getdate(self.start_date) > getdate(structure.effective_to):
			frappe.throw(_("KPI Structure is not effective on the Assignment Start Date."))

	def validate_overlap(self):
		if not self.employee or not self.start_date or not self.end_date:
			return
		overlap = frappe.db.sql(
			"""
			select name
			from `tabKPI Structure Assignment`
			where employee = %(employee)s
				and name != %(name)s
				and docstatus = 1
				and status = 'Active'
				and start_date <= %(end_date)s
				and end_date >= %(start_date)s
			limit 1
			""",
			{
				"employee": self.employee,
				"name": self.name or "",
				"start_date": self.start_date,
				"end_date": self.end_date,
			},
			as_dict=True,
		)
		if overlap:
			frappe.throw(_("Employee already has an overlapping Active KPI Structure Assignment: {0}").format(overlap[0].name))
