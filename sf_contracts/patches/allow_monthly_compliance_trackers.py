import re

import frappe


def execute():
	if not frappe.db.exists("DocType", "Contract Compliance Tracker"):
		return

	frappe.db.set_value(
		"DocField",
		{"parent": "Contract Compliance Tracker", "fieldname": "contract"},
		"unique",
		0,
		update_modified=False,
	)

	for index_name in get_contract_unique_indexes():
		if re.match(r"^[A-Za-z0-9_]+$", index_name):
			frappe.db.sql(f"alter table `tabContract Compliance Tracker` drop index `{index_name}`")

	frappe.clear_cache(doctype="Contract Compliance Tracker")


def get_contract_unique_indexes():
	indexes = frappe.db.sql(
		"""
		show index from `tabContract Compliance Tracker`
		where Column_name = 'contract' and Non_unique = 0 and Key_name != 'PRIMARY'
		""",
		as_dict=True,
	)
	return {index.Key_name for index in indexes}
