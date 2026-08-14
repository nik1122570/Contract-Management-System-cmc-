import frappe


LIFECYCLE_OPTIONS = "Active\nExpired\nTerminated"
STATUS_MAP = {
	"Draft": "Active",
	"Pending": "Active",
	"Pending Execution": "Active",
	"Executed – Awaiting Commencement": "Active",
	"Expired – Services Continuing": "Expired",
	"Expired â€“ Services Continuing": "Expired",
	"Completed": "Active",
	"Closed": "Active",
}


def execute():
	if not frappe.db.has_column("Contract", "sf_contract_lifecycle_status"):
		return

	for old_status, new_status in STATUS_MAP.items():
		frappe.db.sql(
			"""
			update `tabContract`
			set sf_contract_lifecycle_status = %s
			where sf_contract_lifecycle_status = %s
			""",
			(new_status, old_status),
		)

	frappe.db.sql(
		"""
		update `tabContract`
		set sf_contract_lifecycle_status = 'Active'
		where ifnull(sf_contract_lifecycle_status, '') = ''
		"""
	)

	frappe.db.set_value(
		"Custom Field",
		"Contract-sf_contract_lifecycle_status",
		{
			"options": LIFECYCLE_OPTIONS,
			"default": "Active",
		},
		update_modified=False,
	)

	if frappe.db.exists("Property Setter", {"doc_type": "Contract", "property": "field_order"}):
		frappe.clear_cache(doctype="Contract")

	recalculate_lifecycle_statuses()
	frappe.clear_cache(doctype="Contract")


def recalculate_lifecycle_statuses():
	from sf_contracts.contract_lifecycle import get_contract_health_score, get_lifecycle_status

	has_health_score = frappe.db.has_column("Contract", "sf_contract_health_score")
	has_health_reason = frappe.db.has_column("Contract", "sf_contract_health_reason")

	fields = [
		"name",
		"docstatus",
		"is_signed",
		"start_date",
		"end_date",
		"sf_contract_lifecycle_status",
	]

	for optional in (
		"sf_signed_contract_document",
		"requires_fulfilment",
		"sf_compliance_tracker",
		"sf_termination_date",
		"sf_termination_reason",
	):
		if frappe.db.has_column("Contract", optional):
			fields.append(optional)

	if has_health_score:
		fields.append("sf_contract_health_score")
	if has_health_reason:
		fields.append("sf_contract_health_reason")

	for contract in frappe.get_all("Contract", fields=fields):
		updates = {"sf_contract_lifecycle_status": get_lifecycle_status(contract)}

		if has_health_score:
			score, reason = get_contract_health_score(contract)
			updates["sf_contract_health_score"] = score
			if has_health_reason:
				updates["sf_contract_health_reason"] = reason

		frappe.db.set_value("Contract", contract.name, updates, update_modified=False)
