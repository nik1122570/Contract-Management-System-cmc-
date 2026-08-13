import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

from sf_contracts.contract_compliance import ensure_contract_compliance_tracker


def execute():
	make_property_setter(
		"Contract",
		"requires_fulfilment",
		"default",
		"1",
		"Check",
	)
	make_property_setter(
		"Contract",
		"requires_fulfilment",
		"read_only",
		"1",
		"Check",
	)

	if frappe.db.has_column("Contract", "requires_fulfilment"):
		frappe.db.sql(
			"""
			update `tabContract`
			set requires_fulfilment = 1
			where ifnull(requires_fulfilment, 0) = 0
			"""
		)
		create_missing_compliance_trackers()

	if frappe.db.exists("DocType", "Contract Compliance Tracker"):
		frappe.db.set_value(
			"DocField",
			{
				"parent": "Contract Compliance Tracker",
				"fieldname": "evaluation_date",
			},
			{
				"read_only": 1,
				"default": "Today",
			},
			update_modified=False,
		)

	frappe.clear_cache(doctype="Contract")
	frappe.clear_cache(doctype="Contract Compliance Tracker")


def create_missing_compliance_trackers():
	if not frappe.db.has_column("Contract", "sf_compliance_tracker"):
		return

	for contract_name in frappe.get_all("Contract", pluck="name"):
		contract = frappe.get_doc("Contract", contract_name)
		contract.requires_fulfilment = 1
		ensure_contract_compliance_tracker(contract)
