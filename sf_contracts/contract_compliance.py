import frappe
from frappe import _
from frappe.utils import nowdate


def validate_contract_compliance_requirements(doc, method=None):
	if not getattr(doc, "requires_fulfilment", 0):
		return

	tracker_name = get_contract_compliance_tracker(doc)
	if not tracker_name:
		tracker_name = ensure_contract_compliance_tracker(doc)

	tracker_link = frappe.utils.get_link_to_form("Contract Compliance Tracker", tracker_name)
	tracker = frappe.get_doc("Contract Compliance Tracker", tracker_name)
	rows = tracker.get("table_ewpx") or []

	if not rows:
		frappe.throw(
			_(
				"Please fill the Compliance Tracker {0} before submitting this Contract. Add at least one compliance obligation."
			).format(tracker_link),
			title=_("Compliance Tracker Required"),
		)

	missing_rows = []
	required_fields = {
		"terms": _("Terms"),
		"contractual_obligation": _("Contractual Obligation"),
		"responsible_person": _("Responsible Person"),
		"evidence_required": _("Evidence Required"),
		"compliance_status": _("Compliance Status"),
	}

	for row in rows:
		missing = [
			label
			for fieldname, label in required_fields.items()
			if not (row.get(fieldname) or "").strip()
		]
		if missing:
			missing_rows.append(_("Row {0}: {1}").format(row.idx, ", ".join(missing)))

	if missing_rows:
		frappe.throw(
			_(
				"Please complete the Compliance Tracker {0} before submitting this Contract.<br><br>{1}"
			).format(tracker_link, "<br>".join(missing_rows)),
			title=_("Incomplete Compliance Tracker"),
		)


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


def get_contract_compliance_tracker(doc):
	tracker_name = doc.get("sf_compliance_tracker")
	if tracker_name and frappe.db.exists("Contract Compliance Tracker", tracker_name):
		return tracker_name

	return frappe.db.get_value(
		"Contract Compliance Tracker",
		{"contract": doc.name},
		"name",
		order_by="evaluation_date desc, creation desc",
	)


def _set_if_field_exists(doc, fieldname, value):
	if doc.meta.has_field(fieldname):
		doc.set(fieldname, value)


def _update_tracker_counts(tracker_name):
	if not tracker_name or not frappe.db.exists("Contract Compliance Tracker", tracker_name):
		return
