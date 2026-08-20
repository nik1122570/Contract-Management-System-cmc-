import frappe


def execute():
	visible_fields = {
		"contract",
		"company",
		"party_name",
		"contract_type",
		"compliance_percentage",
	}
	hidden_fields = {
		"contractor",
		"evaluation_date",
		"naming_series",
	}

	for fieldname in visible_fields:
		frappe.db.set_value(
			"DocField",
			{"parent": "Contract Compliance Tracker", "fieldname": fieldname},
			"in_list_view",
			1,
			update_modified=False,
		)

	for fieldname in hidden_fields:
		frappe.db.set_value(
			"DocField",
			{"parent": "Contract Compliance Tracker", "fieldname": fieldname},
			"in_list_view",
			0,
			update_modified=False,
		)

	frappe.db.set_value(
		"DocField",
		{"parent": "Contract Compliance Tracker", "fieldname": "party_name"},
		"label",
		"Party Name",
		update_modified=False,
	)
	frappe.clear_cache(doctype="Contract Compliance Tracker")
