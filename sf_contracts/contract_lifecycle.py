import frappe
from frappe import _
from frappe.utils import getdate, nowdate


FINAL_STATUSES = {"Closed", "Terminated"}
MANUAL_STATUSES = FINAL_STATUSES | {"Expired – Services Continuing"}
LEGACY_STATUS_MAP = {
	"Pending": "Pending Execution",
	"Expired": "Expired – Services Continuing",
	"Completed": "Closed",
}


def set_submitted_for_signing_on_draft(doc):
	if not hasattr(doc, "submitted_for_signing"):
		return

	if doc.docstatus == 0:
		doc.submitted_for_signing = 1


def validate_signed_contract_document(doc):
	if not hasattr(doc, "sf_signed_contract_document"):
		return

	if doc.get("is_signed") and not doc.get("sf_signed_contract_document"):
		frappe.throw(
			_(
				"Attach the signed contract file in <b>Signed Contract Document</b> before marking this Contract as signed."
			)
		)


def get_lifecycle_status(contract) -> str:
	current_status = LEGACY_STATUS_MAP.get(
		contract.get("sf_contract_lifecycle_status"),
		contract.get("sf_contract_lifecycle_status"),
	)

	if current_status in MANUAL_STATUSES:
		return current_status

	if contract.get("docstatus") == 0:
		return "Draft"

	if not contract.get("is_signed"):
		return "Pending Execution"

	today = getdate(nowdate())
	start_date = getdate(contract.start_date) if contract.get("start_date") else None
	end_date = getdate(contract.end_date) if contract.get("end_date") else None

	if end_date and today > end_date:
		return "Expired – Services Continuing"

	if start_date and today < start_date:
		return "Executed – Awaiting Commencement"

	return "Active"


def update_contract_lifecycle_status(doc, method=None):
	set_submitted_for_signing_on_draft(doc)

	if not hasattr(doc, "sf_contract_lifecycle_status"):
		return

	validate_signed_contract_document(doc)
	doc.sf_contract_lifecycle_status = get_lifecycle_status(doc)


def update_lifecycle_status_for_contracts():
	if not frappe.db.has_column("Contract", "sf_contract_lifecycle_status"):
		return

	contracts = frappe.get_all(
		"Contract",
		fields=[
			"name",
			"docstatus",
			"is_signed",
			"start_date",
			"end_date",
			"sf_contract_lifecycle_status",
		],
	)

	for contract in contracts:
		new_status = get_lifecycle_status(contract)
		if contract.sf_contract_lifecycle_status != new_status:
			frappe.db.set_value(
				"Contract",
				contract.name,
				"sf_contract_lifecycle_status",
				new_status,
				update_modified=False,
			)


def update_submitted_for_signing_for_draft_contracts():
	if not frappe.db.has_column("Contract", "submitted_for_signing"):
		return

	for contract in frappe.get_all(
		"Contract",
		filters={"docstatus": 0, "submitted_for_signing": 0},
		pluck="name",
	):
		frappe.db.set_value(
			"Contract",
			contract,
			"submitted_for_signing",
			1,
			update_modified=False,
		)
