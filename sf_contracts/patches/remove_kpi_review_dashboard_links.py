import frappe


def execute():
	frappe.db.delete("DocType Link", {"parent": "KPI Review"})
	frappe.clear_cache(doctype="KPI Review")
