# Copyright (c) 2026, Nickson John and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ContractComplianceTracker(Document):
	def validate(self):
		self.validate_empty_obligation_rows()

	def validate_empty_obligation_rows(self):
		table_fields = (
			("table_ewpx", _("Obligation Table 1")),
			("table_jpcz", _("Obligation Table 2")),
			("table_dhlt", _("Obligation Table 3")),
			("table_mmyd", _("Obligation 4")),
		)

		for fieldname, label in table_fields:
			for row in self.get(fieldname) or []:
				if self.is_empty_obligation_row(row):
					frappe.throw(
						_("{0}, row {1} is empty. Please fill in the row or delete it before saving.").format(
							label, row.idx
						),
						title=_("Empty Obligation Row"),
					)

	def is_empty_obligation_row(self, row):
		obligation_fields = (
			"contractual_obligation",
			"responsible_person",
			"evidence_required",
			"compliance_status",
			"remarks__action",
		)

		return not any((row.get(fieldname) or "").strip() for fieldname in obligation_fields)
