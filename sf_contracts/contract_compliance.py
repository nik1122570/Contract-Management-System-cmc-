import frappe
from frappe.utils import nowdate


def validate_contract_compliance_requirements(doc, method=None):
	return


def ensure_contract_compliance_tracker(doc, method=None):
	if not getattr(doc, "requires_fulfilment", 0):
		return

	existing_tracker = doc.get("sf_compliance_tracker") or frappe.db.get_value(
		"Contract Compliance Tracker", {"contract": doc.name}, "name"
	)

	if existing_tracker:
		if doc.get("sf_compliance_tracker") != existing_tracker:
			frappe.db.set_value(
				"Contract",
				doc.name,
				"sf_compliance_tracker",
				existing_tracker,
				update_modified=False,
			)
		return existing_tracker

	tracker = frappe.new_doc("Contract Compliance Tracker")
	tracker.contract = doc.name
	_set_if_field_exists(tracker, "evaluation_date", nowdate())
	_set_if_field_exists(tracker, "party_type", doc.get("party_type"))
	_set_if_field_exists(tracker, "party_name", doc.get("party_name"))
	_set_if_field_exists(tracker, "contract_type", doc.get("sf_contract_type"))
	_set_if_field_exists(tracker, "contractor", doc.get("sf_contractor"))
	tracker.insert(ignore_permissions=True)

	_update_tracker_counts(tracker.name)

	if frappe.db.has_column("Contract", "sf_compliance_tracker"):
		frappe.db.set_value(
			"Contract",
			doc.name,
			"sf_compliance_tracker",
			tracker.name,
			update_modified=False,
		)

	return tracker.name


def _set_if_field_exists(doc, fieldname, value):
	if doc.meta.has_field(fieldname):
		doc.set(fieldname, value)


def _update_tracker_counts(tracker_name):
	if not tracker_name or not frappe.db.exists("Contract Compliance Tracker", tracker_name):
		return
