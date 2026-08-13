import frappe


CATEGORIES = [
	{
		"category_name": "Annual Returns",
		"description": "Company annual returns, filing deadlines, financial year approval and related costs.",
		"default_frequency": "Annual",
		"requires_license_no": 1,
		"requires_period": 1,
		"requires_due_date": 1,
		"requires_amount": 1,
		"fields": [
			{"field_label": "Incorporation Date", "field_key": "incorporation_date", "field_type": "Date"},
			{"field_label": "Financial Year 2025", "field_key": "financial_year_2025", "field_type": "Data"},
			{"field_label": "Financial Year 2026", "field_key": "financial_year_2026", "field_type": "Data"},
		],
	},
	{
		"category_name": "Business Licence",
		"description": "Business licences issued by municipal, district or other licensing authorities.",
		"default_frequency": "Renewal Based",
		"requires_authority": 1,
		"requires_license_no": 1,
		"requires_issue_date": 1,
		"requires_expiry_date": 1,
		"requires_amount": 1,
		"requires_attachment": 1,
		"fields": [
			{"field_label": "Nature of Business", "field_key": "nature_of_business", "field_type": "Small Text"},
		],
	},
	{
		"category_name": "Local Content",
		"description": "Local content reports, plans, acknowledgements and submission status.",
		"default_frequency": "Quarterly",
		"requires_period": 1,
		"requires_due_date": 1,
		"requires_attachment": 1,
		"fields": [
			{"field_label": "Report Type", "field_key": "report_type", "field_type": "Data", "is_required": 1},
			{"field_label": "Acknowledgement Reference", "field_key": "acknowledgement_reference", "field_type": "Data"},
		],
	},
	{
		"category_name": "Statutory Compliance",
		"description": "Monthly statutory obligations such as NSSF, WCF, PAYE and other recurring payments.",
		"default_frequency": "Monthly",
		"requires_month_year": 1,
		"fields": [
			{"field_label": "Payment Reference", "field_key": "payment_reference", "field_type": "Data"},
			{"field_label": "Receipt / Control Number", "field_key": "receipt_or_control_number", "field_type": "Data"},
		],
	},
	{
		"category_name": "Certificate",
		"description": "Certificates, ISO, OSHA and other compliance certificates with expiry tracking.",
		"default_frequency": "Renewal Based",
		"requires_issue_date": 1,
		"requires_expiry_date": 1,
		"requires_attachment": 1,
		"fields": [
			{"field_label": "Certificate / ISO", "field_key": "certificate_or_iso", "field_type": "Data"},
		],
	},
	{
		"category_name": "Data Protection",
		"description": "Data protection registration and renewal tracking.",
		"default_frequency": "Renewal Based",
		"requires_issue_date": 1,
		"requires_expiry_date": 1,
		"requires_attachment": 1,
		"fields": [
			{"field_label": "Registration Reference", "field_key": "registration_reference", "field_type": "Data"},
		],
	},
	{
		"category_name": "Trademark",
		"description": "Trademark applications, registrations, classes, covered goods and renewal dates.",
		"default_frequency": "Renewal Based",
		"requires_issue_date": 1,
		"requires_expiry_date": 1,
		"requires_attachment": 1,
		"fields": [
			{"field_label": "Trademark Description", "field_key": "trademark_description", "field_type": "Small Text", "is_required": 1},
			{"field_label": "Class", "field_key": "trademark_class", "field_type": "Data"},
			{"field_label": "Goods / Services Covered", "field_key": "goods_services_covered", "field_type": "Small Text"},
		],
	},
	{
		"category_name": "Mining License",
		"description": "Mining and prospecting licences, locations, partners, mine type and expiry tracking.",
		"default_frequency": "Renewal Based",
		"requires_license_no": 1,
		"requires_effective_date": 1,
		"requires_expiry_date": 1,
		"requires_attachment": 1,
		"fields": [
			{"field_label": "Granted To", "field_key": "granted_to", "field_type": "Data"},
			{"field_label": "Partnership With", "field_key": "partnership_with", "field_type": "Small Text"},
			{"field_label": "Nature of Mine", "field_key": "nature_of_mine", "field_type": "Data"},
			{"field_label": "Location", "field_key": "location", "field_type": "Small Text"},
		],
	},
]


def execute():
	for category_data in CATEGORIES:
		category_values = category_data.copy()
		fields = category_values.pop("fields")

		if frappe.db.exists("Compliance Category", category_values["category_name"]):
			category = frappe.get_doc("Compliance Category", category_values["category_name"])
			category.update(category_values)
			category.set("fields", [])
		else:
			category = frappe.new_doc("Compliance Category")
			category.update(category_values)

		for field in fields:
			category.append("fields", field)

		category.save(ignore_permissions=True)

	frappe.db.commit()
