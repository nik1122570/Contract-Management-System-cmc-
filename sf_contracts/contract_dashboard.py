from frappe import _


def get_data(data=None):
	data = data or {}
	data.setdefault("fieldname", "contract")
	data.setdefault("transactions", [])
	data.setdefault("non_standard_fieldnames", {})
	data["non_standard_fieldnames"]["Contract Compliance Tracker"] = "contract"

	_add_transaction(data, _("Compliance"), ["Contract Compliance Tracker"])
	return data


def _add_transaction(data, label, items):
	for transaction in data["transactions"]:
		if transaction.get("label") == label:
			for item in items:
				if item not in transaction.get("items", []):
					transaction.setdefault("items", []).append(item)
			return

	data["transactions"].append({"label": label, "items": items})
