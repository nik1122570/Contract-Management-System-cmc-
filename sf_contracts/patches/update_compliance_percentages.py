import frappe


def execute():
	if not frappe.db.has_column("Contract Compliance Tracker", "compliance_percentage"):
		return

	for name in frappe.get_all("Contract Compliance Tracker", pluck="name"):
		tracker = frappe.get_doc("Contract Compliance Tracker", name)
		tracker.set_compliance_percentage()
		tracker.db_set("compliance_percentage", tracker.compliance_percentage, update_modified=False)
