import frappe


def execute():
	if not frappe.db.exists("DocType", "Compliance Settings"):
		return

	settings = frappe.get_single("Compliance Settings")
	settings.critical_days = settings.critical_days or 7
	settings.high_days = settings.high_days or 30
	settings.medium_days = settings.medium_days or 90
	settings.save(ignore_permissions=True)
	frappe.db.commit()
