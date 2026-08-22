import frappe
from frappe.model.document import Document


class KPIPerspective(Document):
	def validate(self):
		self.perspective_name = (self.perspective_name or "").strip()
		if not self.perspective_name:
			frappe.throw("Perspective Name is required.")

