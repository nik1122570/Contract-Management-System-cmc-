import frappe


SF_COMPANIES = [
	"AKO GROUP LIMITED",
	"CHERRY GARMENTS AND SAFETY SOLUTIONS LIMITED",
	"EAST AFRICA HAULIERS LIMITED",
	"EQUPOINT PROPERTIES LIMITED",
	"GREAT VISION ADVENTURES LIMITED",
	"OVEC INTERNATIONAL LIMITED",
	"RADIANCE FINANCE LIMITED",
	"RADIANCE INSURANCE LIMITED",
	"RAKOLI SYSTEMS LIMITED",
	"SF GROUP OF COMPANIES LIMITED",
	"SF SMART ENERGY COMPANY LIMITED",
	"SF ULINZI LIMITED",
	"SILVER ENTERTRADE LIMITED",
	"STRATEGIC BUSINESS SOLUTIONS LIMITED",
]


def execute():
	for company_name in SF_COMPANIES:
		if frappe.db.exists("SF Companies", company_name):
			continue

		company = frappe.new_doc("SF Companies")
		company.company_name = company_name
		company.status = "Active"
		company.insert(ignore_permissions=True)

	frappe.db.commit()
