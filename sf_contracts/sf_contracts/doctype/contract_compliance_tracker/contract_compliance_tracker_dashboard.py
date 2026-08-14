from frappe import _


def get_data():
	return {
		"fieldname": "contract",
		"internal_links": {
			"Contract": "contract",
		},
		"transactions": [
			{"label": _("Originating Document"), "items": ["Contract"]},
		],
	}
