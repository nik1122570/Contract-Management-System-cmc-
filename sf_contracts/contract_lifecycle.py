import frappe
from frappe import _
from frappe.utils import date_diff, getdate, nowdate


FINAL_STATUSES = {"Terminated"}
MANUAL_STATUSES = FINAL_STATUSES
LEGACY_STATUS_MAP = {
	"Draft": "Active",
	"Pending": "Active",
	"Pending Execution": "Active",
	"Executed – Awaiting Commencement": "Active",
	"Expired – Services Continuing": "Expired",
	"Expired â€“ Services Continuing": "Expired",
	"Completed": "Active",
	"Closed": "Active",
}
EXPIRY_ATTENTION_DAYS = 30


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

	today = getdate(nowdate())
	end_date = getdate(contract.end_date) if contract.get("end_date") else None

	if end_date and today > end_date:
		return "Expired"

	return "Active"


def update_contract_lifecycle_status(doc, method=None):
	set_submitted_for_signing_on_draft(doc)
	set_requires_fulfilment_for_contract(doc)

	if not hasattr(doc, "sf_contract_lifecycle_status"):
		return

	validate_signed_contract_document(doc)
	doc.sf_contract_lifecycle_status = get_lifecycle_status(doc)
	set_contract_health_score(doc)


def set_requires_fulfilment_for_contract(doc):
	if not hasattr(doc, "requires_fulfilment"):
		return

	doc.requires_fulfilment = 1


def set_contract_health_score(doc):
	if not hasattr(doc, "sf_contract_health_score"):
		return

	score, reason = get_contract_health_score(doc)
	doc.sf_contract_health_score = score

	if hasattr(doc, "sf_contract_health_reason"):
		doc.sf_contract_health_reason = reason


def get_contract_health_score(contract) -> tuple[str, str]:
	status = contract.get("sf_contract_lifecycle_status") or get_lifecycle_status(contract)
	today = getdate(nowdate())
	end_date = getdate(contract.end_date) if contract.get("end_date") else None
	days_to_expiry = date_diff(end_date, today) if end_date else None
	compliance_percentage = get_contract_compliance_percentage(contract)

	if status == "Expired":
		return "Critical", _("Contract has expired.")

	if contract.get("is_signed") and not contract.get("sf_signed_contract_document"):
		return "Critical", _("Contract is marked signed but the signed document is missing.")

	if status == "Terminated" and (
		not contract.get("sf_termination_date") or not contract.get("sf_termination_reason")
	):
		return "Critical", _("Terminated contract is missing termination date or reason.")

	if compliance_percentage is not None and compliance_percentage < 70:
		return "Critical", _("Compliance is only {0}%.").format(compliance_percentage)

	if contract.get("requires_fulfilment") and not contract.get("sf_compliance_tracker"):
		return "Attention Needed", _("Requires fulfilment but no compliance tracker is linked.")

	if compliance_percentage is not None and compliance_percentage < 100:
		return "Attention Needed", _("Compliance is {0}%.").format(compliance_percentage)

	if days_to_expiry is not None and 0 <= days_to_expiry <= EXPIRY_ATTENTION_DAYS:
		return "Attention Needed", _("Contract expires in {0} days.").format(days_to_expiry)

	if not contract.get("is_signed"):
		return "Attention Needed", _("Contract is not yet signed.")

	return "Healthy", _("No immediate contract risk detected.")


def is_expired_services_continuing(status):
	return status in ("Expired", "Expired – Services Continuing", "Expired â€“ Services Continuing")


def get_contract_compliance_percentage(contract):
	tracker = contract.get("sf_compliance_tracker")

	if not tracker and contract.get("name"):
		tracker = frappe.db.get_value("Contract Compliance Tracker", {"contract": contract.name}, "name")

	if not tracker:
		return None

	if get_contract_compliance_obligation_count(tracker) == 0:
		return None

	percentage = frappe.db.get_value("Contract Compliance Tracker", tracker, "compliance_percentage")

	if percentage is None:
		return None

	return round(float(percentage))


def get_contract_compliance_obligation_count(tracker):
	return frappe.db.count(
		"Contract Table 1",
		{
			"parent": tracker,
			"parenttype": "Contract Compliance Tracker",
			"parentfield": "table_ewpx",
		},
	)


def update_lifecycle_status_for_contracts():
	if not frappe.db.has_column("Contract", "sf_contract_lifecycle_status"):
		return

	has_health_score = frappe.db.has_column("Contract", "sf_contract_health_score")
	has_health_reason = frappe.db.has_column("Contract", "sf_contract_health_reason")
	optional_fields = [
		fieldname
		for fieldname in (
			"sf_signed_contract_document",
			"requires_fulfilment",
			"sf_compliance_tracker",
			"sf_termination_date",
			"sf_termination_reason",
		)
		if frappe.db.has_column("Contract", fieldname)
	]
	contracts = frappe.get_all(
		"Contract",
		fields=[
			"name",
			"docstatus",
			"is_signed",
			"start_date",
			"end_date",
			"sf_contract_lifecycle_status",
			*optional_fields,
			*(["sf_contract_health_score"] if has_health_score else []),
			*(["sf_contract_health_reason"] if has_health_reason else []),
		],
	)

	for contract in contracts:
		old_status = contract.get("sf_contract_lifecycle_status")
		new_status = get_lifecycle_status(contract)
		contract.sf_contract_lifecycle_status = new_status
		updates = {}

		if old_status != new_status:
			updates["sf_contract_lifecycle_status"] = new_status

		if has_health_score:
			new_health_score, new_health_reason = get_contract_health_score(contract)

			if contract.get("sf_contract_health_score") != new_health_score:
				updates["sf_contract_health_score"] = new_health_score

			if has_health_reason and contract.get("sf_contract_health_reason") != new_health_reason:
				updates["sf_contract_health_reason"] = new_health_reason

		if updates:
			frappe.db.set_value(
				"Contract",
				contract.name,
				updates,
				update_modified=False,
			)


def update_contract_health_score_in_db(contract_name):
	if not contract_name or not frappe.db.exists("Contract", contract_name):
		return

	if not frappe.db.has_column("Contract", "sf_contract_health_score"):
		return

	contract = frappe.get_doc("Contract", contract_name)
	set_contract_health_score(contract)
	frappe.db.set_value(
		"Contract",
		contract.name,
		{
			"sf_contract_health_score": contract.get("sf_contract_health_score"),
			"sf_contract_health_reason": contract.get("sf_contract_health_reason"),
		},
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
