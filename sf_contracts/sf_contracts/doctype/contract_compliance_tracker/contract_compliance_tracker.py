# Copyright (c) 2026, Nickson John and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ContractComplianceTracker(Document):
	def validate(self):
		self.sync_contract_fields()
		self.set_compliance_percentage()
		self.validate_empty_obligation_rows()

	def on_update(self):
		if self.contract:
			from sf_contracts.contract_lifecycle import update_contract_health_score_in_db

			update_contract_health_score_in_db(self.contract)

	def sync_contract_fields(self):
		if not self.contract:
			return

		contract_values = frappe.db.get_value(
			"Contract",
			self.contract,
			["sf_contract_type", "sf_contractor"],
			as_dict=True,
		)

		if not contract_values:
			return

		self.contract_type = contract_values.get("sf_contract_type")
		self.contractor = contract_values.get("sf_contractor")

	def set_compliance_percentage(self):
		table_fields = ("table_ewpx", "table_jpcz", "table_dhlt", "table_mmyd")
		total = 0
		compliant = 0

		for fieldname in table_fields:
			for row in self.get(fieldname) or []:
				total += 1

				if self.get_compliance_status_class(row.get("compliance_status")) == "compliant":
					compliant += 1

		self.compliance_percentage = round((compliant / total) * 100) if total else 0

	def get_compliance_status_class(self, value):
		normalized = " ".join((value or "").lower().split())

		if normalized == "compliant":
			return "compliant"

		if normalized in ("non- compliant", "non-compliant"):
			return "non-compliant"

		return "pending"

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
