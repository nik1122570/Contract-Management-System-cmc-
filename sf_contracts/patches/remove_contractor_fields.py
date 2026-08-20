import frappe

from sf_contracts.setup_contract_fields import sync_contract_field_order


def execute():
	remove_contract_contractor_field()
	remove_compliance_tracker_contractor_field()
	sync_contract_field_order()
	frappe.clear_cache(doctype="Contract")
	frappe.clear_cache(doctype="Contract Compliance Tracker")


def remove_contract_contractor_field():
	for custom_field in frappe.get_all(
		"Custom Field",
		filters={"dt": "Contract", "fieldname": "sf_contractor"},
		pluck="name",
	):
		frappe.db.delete("Property Setter", {"doc_type": "Contract", "field_name": "sf_contractor"})
		frappe.db.delete("Custom Field", {"name": custom_field})

	frappe.db.delete("Property Setter", {"doc_type": "Contract", "field_name": "sf_contractor"})


def remove_compliance_tracker_contractor_field():
	frappe.db.delete(
		"DocField",
		{"parent": "Contract Compliance Tracker", "fieldname": "contractor"},
	)
	frappe.db.delete(
		"Property Setter",
		{"doc_type": "Contract Compliance Tracker", "field_name": "contractor"},
	)
