import frappe


def execute():
	if not frappe.db.exists("DocType", "Compliance Register"):
		return

	for name in frappe.get_all("Compliance Register", pluck="name"):
		doc = frappe.get_doc("Compliance Register", name)
		doc.set_days_to_expiry()
		doc.set_priority()
		doc.db_set(
			{
				"days_to_expiry": doc.days_to_expiry,
				"priority": doc.priority,
			},
			update_modified=False,
		)

	frappe.db.commit()
