import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, flt, now_datetime, today


class KPIReview(Document):
	def validate(self):
		self.set_totals()
		self.validate_rating_bounds()
		self.set_rating_category()

	def before_submit(self):
		if self.workflow_status != "Completed":
			frappe.throw(_("Only Completed KPI Reviews can be submitted."))
		self.validate_final_review_complete()

	def set_totals(self):
		self.total_weight = sum(flt(row.weight) for row in self.review_items)
		self.self_total = sum(flt(row.self_rating) for row in self.review_items)
		self.final_total = sum(flt(row.final_rating) for row in self.review_items)

	def validate_rating_bounds(self):
		for row in self.review_items:
			if flt(row.self_rating) < 0 or flt(row.final_rating) < 0:
				frappe.throw(_("Row {0}: Ratings cannot be negative.").format(row.idx))
			if flt(row.self_rating) > flt(row.weight):
				frappe.throw(_("Row {0}: Self Rating cannot exceed Weight.").format(row.idx))
			if flt(row.final_rating) > flt(row.weight):
				frappe.throw(_("Row {0}: Final Rating cannot exceed Weight.").format(row.idx))

	def set_rating_category(self):
		score = flt(self.final_total if self.workflow_status == "Completed" else self.self_total)
		if score >= 90:
			self.rating_category = "Outstanding"
		elif score >= 80:
			self.rating_category = "Very Good"
		elif score >= 70:
			self.rating_category = "Good"
		elif score >= 60:
			self.rating_category = "Needs Improvement"
		else:
			self.rating_category = "Unsatisfactory"

	def validate_self_review_complete(self):
		for row in self.review_items:
			if row.evidence_required and not (row.evidence or row.evidence_comment):
				frappe.throw(_("Row {0}: Evidence or Evidence Comment is required.").format(row.idx))
			if row.self_rating is None:
				frappe.throw(_("Row {0}: Self Rating is required.").format(row.idx))

	def validate_final_review_complete(self):
		for row in self.review_items:
			if row.final_rating is None:
				frappe.throw(_("Row {0}: Final Rating is required.").format(row.idx))
			if flt(row.final_rating) != flt(row.self_rating) and not row.reviewer_comment:
				frappe.throw(_("Row {0}: Reviewer Comment is required when Final Rating differs from Self Rating.").format(row.idx))
		if not self.final_reviewer_summary:
			frappe.throw(_("Final Reviewer Summary is required."))

	def _is_employee_user(self):
		return self.employee_user and frappe.session.user == self.employee_user

	def _can_final_review(self):
		return any(frappe.has_role(role) for role in ("System Manager", "KPI Manager", "KPI Final Reviewer"))

	@frappe.whitelist()
	def self_submit(self):
		if self.workflow_status != "Pending Self Rating":
			frappe.throw(_("This KPI Review is not pending self rating."))
		if not (self._is_employee_user() or frappe.has_role("System Manager")):
			frappe.throw(_("Only the assigned employee can submit the self rating."))
		if not self.employee_summary:
			frappe.throw(_("Employee Summary is required."))

		self.validate_self_review_complete()
		self.workflow_status = "Pending Final Rating"
		self.employee_accepted = 1
		self.employee_accepted_by = frappe.session.user
		self.employee_accepted_on = now_datetime()
		if not self.final_rating_due_date:
			self.final_rating_due_date = add_days(today(), 7)
		self.save()
		return self.name

	@frappe.whitelist()
	def return_to_employee(self, reason=None):
		if not self._can_final_review():
			frappe.throw(_("Only a KPI Final Reviewer or KPI Manager can return the review."))
		if not reason:
			frappe.throw(_("Return reason is required."))
		self.workflow_status = "Pending Self Rating"
		self.return_reason = reason
		self.save()
		self.add_comment("Comment", _("Returned to employee: {0}").format(reason))
		return self.name

	@frappe.whitelist()
	def complete_review(self):
		if not self._can_final_review():
			frappe.throw(_("Only a KPI Final Reviewer or KPI Manager can complete the review."))
		if self.workflow_status != "Pending Final Rating":
			frappe.throw(_("This KPI Review is not pending final rating."))

		self.validate_final_review_complete()
		self.workflow_status = "Completed"
		self.final_reviewed_by = frappe.session.user
		self.final_reviewed_on = now_datetime()
		self.set_totals()
		self.set_rating_category()
		if self.docstatus == 0:
			self.submit()
		else:
			self.save()
		return self.name

