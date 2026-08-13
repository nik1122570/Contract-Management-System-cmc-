# Copyright (c) 2026, Nickson John and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ComplianceSettings(Document):
	def validate(self):
		if self.critical_days > self.high_days:
			frappe.throw(
				_("Critical Within Days cannot be greater than High Within Days."),
				title=_("Invalid Priority Thresholds"),
			)

		if self.high_days > self.medium_days:
			frappe.throw(
				_("High Within Days cannot be greater than Medium Within Days."),
				title=_("Invalid Priority Thresholds"),
			)
