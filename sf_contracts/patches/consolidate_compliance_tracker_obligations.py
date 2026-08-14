import frappe


OLD_TABLE_FIELDS = ("table_jpcz", "table_dhlt", "table_mmyd")
CURRENT_TABLE_FIELD = "table_ewpx"


def execute():
	if not frappe.db.exists("DocType", "Contract Compliance Tracker"):
		return

	for tracker in frappe.get_all("Contract Compliance Tracker", pluck="name"):
		move_old_rows_to_current_table(tracker)

	frappe.clear_cache(doctype="Contract Compliance Tracker")


def move_old_rows_to_current_table(tracker):
	current_count = frappe.db.count(
		"Contract Table 1",
		{
			"parent": tracker,
			"parenttype": "Contract Compliance Tracker",
			"parentfield": CURRENT_TABLE_FIELD,
		},
	)

	for old_parentfield in OLD_TABLE_FIELDS:
		rows = frappe.get_all(
			"Contract Table 1",
			filters={
				"parent": tracker,
				"parenttype": "Contract Compliance Tracker",
				"parentfield": old_parentfield,
			},
			fields=["name"],
			order_by="idx asc",
		)

		for row in rows:
			current_count += 1
			frappe.db.set_value(
				"Contract Table 1",
				row.name,
				{
					"parentfield": CURRENT_TABLE_FIELD,
					"idx": current_count,
				},
				update_modified=False,
			)

	update_tracker_percentage(tracker)


def update_tracker_percentage(tracker):
	doc = frappe.get_doc("Contract Compliance Tracker", tracker)
	doc.set_compliance_percentage()
	frappe.db.set_value(
		"Contract Compliance Tracker",
		tracker,
		"compliance_percentage",
		doc.compliance_percentage,
		update_modified=False,
	)
