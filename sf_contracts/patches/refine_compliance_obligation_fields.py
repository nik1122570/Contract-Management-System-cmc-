import frappe


def execute():
	if not frappe.db.exists("DocType", "Contract Table 1"):
		return

	frappe.db.set_value(
		"DocField",
		{"parent": "Contract Table 1", "fieldname": "responsible_person"},
		{
			"fieldtype": "Data",
			"options": "",
		},
		update_modified=False,
	)
	frappe.db.set_value(
		"DocField",
		{"parent": "Contract Table 1", "fieldname": "risk"},
		"options",
		"\nHigh\nMedium\nLow",
		update_modified=False,
	)
	frappe.clear_cache(doctype="Contract Table 1")
	frappe.clear_cache(doctype="Contract Compliance Tracker")
