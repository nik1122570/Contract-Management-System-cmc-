import frappe


def execute():
	create_roles()
	create_default_perspectives()


def create_roles():
	for role in ("KPI Manager", "KPI Employee", "KPI Final Reviewer"):
		if not frappe.db.exists("Role", role):
			doc = frappe.new_doc("Role")
			doc.role_name = role
			doc.desk_access = 1
			doc.insert(ignore_permissions=True)


def create_default_perspectives():
	for perspective in ("Financial", "Customer", "Internal Process", "People", "Leadership"):
		if not frappe.db.exists("KPI Perspective", perspective):
			doc = frappe.new_doc("KPI Perspective")
			doc.perspective_name = perspective
			doc.is_active = 1
			doc.insert(ignore_permissions=True)
