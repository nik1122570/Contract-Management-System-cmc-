import frappe


def execute():
	if not frappe.db.has_column("Contract Compliance Tracker", "contract_type"):
		return

	if not frappe.db.has_column("Contract Compliance Tracker", "contractor"):
		return

	for tracker in frappe.get_all("Contract Compliance Tracker", fields=["name", "contract"]):
		if not tracker.contract:
			continue

		contract_values = frappe.db.get_value(
			"Contract",
			tracker.contract,
			["sf_contract_type", "sf_contractor"],
			as_dict=True,
		)

		if not contract_values:
			continue

		frappe.db.set_value(
			"Contract Compliance Tracker",
			tracker.name,
			{
				"contract_type": contract_values.get("sf_contract_type"),
				"contractor": contract_values.get("sf_contractor"),
			},
			update_modified=False,
		)
