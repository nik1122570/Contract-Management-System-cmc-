from frappe import _


def get_data():
	return {
		"fieldname": "sf_compliance_tracker",
		"non_standard_fieldnames": {
			"Contract": "sf_compliance_tracker",
		},
		"transactions": [
			{"label": _("Linked Documents"), "items": ["Contract"]},
		],
	}
