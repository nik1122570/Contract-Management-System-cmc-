import frappe


LIFECYCLE_OPTIONS = "Draft\nActive\nExpired – Services Continuing\nClosed\nTerminated"


def execute():
	if frappe.db.exists("Custom Field", "Contract-sf_contract_lifecycle_status"):
		frappe.db.set_value(
			"Custom Field",
			"Contract-sf_contract_lifecycle_status",
			"options",
			LIFECYCLE_OPTIONS,
			update_modified=False,
		)

	if frappe.db.has_column("Contract", "sf_contract_lifecycle_status"):
		for status in ("Pending Execution", "Executed – Awaiting Commencement"):
			frappe.db.set_value(
				"Contract",
				{"sf_contract_lifecycle_status": status},
				"sf_contract_lifecycle_status",
				"Draft",
				update_modified=False,
			)

	frappe.clear_cache(doctype="Contract")
	frappe.db.commit()
