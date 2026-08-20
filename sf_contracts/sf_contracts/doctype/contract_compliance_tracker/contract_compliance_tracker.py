# Copyright (c) 2026, Nickson John and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_months, formatdate, getdate


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
			["sf_contract_type"],
			as_dict=True,
		)

		if not contract_values:
			return

		self.contract_type = contract_values.get("sf_contract_type")

	def set_compliance_percentage(self):
		total = 0
		compliant = 0

		for row in self.get("table_ewpx") or []:
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
		for row in self.get("table_ewpx") or []:
			if self.is_empty_obligation_row(row):
				frappe.throw(
					_("Compliance Obligations, row {0} is empty. Please fill in the row or delete it before saving.").format(
						row.idx
					),
					title=_("Empty Obligation Row"),
				)

	def is_empty_obligation_row(self, row):
		obligation_fields = (
			"contractual_obligation",
			"responsible_person",
			"evidence_required",
			"compliance_status",
		)

		return not any((row.get(fieldname) or "").strip() for fieldname in obligation_fields)


@frappe.whitelist()
def create_next_month_tracker(source_name):
	if not source_name:
		frappe.throw(_("Source Contract Compliance Tracker is required."))

	source = frappe.get_doc("Contract Compliance Tracker", source_name)
	source.check_permission("read")

	next_evaluation_date = add_months(getdate(source.evaluation_date), 1)
	existing = frappe.db.get_value(
		"Contract Compliance Tracker",
		{
			"contract": source.contract,
			"evaluation_date": next_evaluation_date,
		},
		"name",
	)

	if existing:
		frappe.throw(
			_("A Contract Compliance Tracker already exists for {0} on {1}.").format(
				source.contract,
				formatdate(next_evaluation_date),
			),
			title=_("Tracker Already Exists"),
		)

	target = frappe.new_doc("Contract Compliance Tracker")
	target.contract = source.contract
	target.evaluation_date = next_evaluation_date
	target.party_name = source.party_name
	target.contract_type = source.contract_type

	for row in source.get("table_ewpx") or []:
		target.append(
			"table_ewpx",
			{
				"risk": row.risk,
				"terms": row.terms,
				"contractual_obligation": row.contractual_obligation,
				"responsible_person": row.responsible_person,
				"evidence_required": row.evidence_required,
				"compliance_status": "",
			},
		)

	target.insert()

	return {
		"name": target.name,
		"evaluation_date": target.evaluation_date,
	}
