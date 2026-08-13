import frappe


STATUS_LABELS = {
	"total": "Total Contracts",
	"pending": "Draft Contracts",
	"active": "Active Contracts",
	"terminated": "Terminated Contracts",
	"expired": "Expired Services Continuing",
	"completed": "Closed Contracts",
}

STATUS_VALUES = {
	"pending": "Draft",
	"active": "Active",
	"terminated": "Terminated",
	"expired": "Expired – Services Continuing",
	"completed": "Closed",
}
HEALTH_VALUES = {
	"critical": "Critical",
	"attention": "Attention Needed",
	"healthy": "Healthy",
}


def _contract_count(status=None):
	filters = {}
	if status:
		filters["sf_contract_lifecycle_status"] = status

	return frappe.db.count("Contract", filters)


def _health_count(health_score=None):
	filters = {}
	if health_score:
		filters["sf_contract_health_score"] = health_score

	return frappe.db.count("Contract", filters)


def _card_payload(key):
	status = STATUS_VALUES.get(key)
	route_options = {}
	value = _contract_count(status)

	if status:
		route_options = {"sf_contract_lifecycle_status": ["=", status]}

	return {
		"value": value,
		"fieldtype": "Int",
		"route": ["List", "Contract"],
		"route_options": route_options,
	}


def _health_card_payload(key):
	health_score = HEALTH_VALUES.get(key)
	route_options = {}
	value = _health_count(health_score)

	if health_score:
		route_options = {"sf_contract_health_score": ["=", health_score]}

	return {
		"value": value,
		"fieldtype": "Int",
		"route": ["List", "Contract"],
		"route_options": route_options,
	}


@frappe.whitelist()
def total_contracts(filters=None):
	return _card_payload("total")


@frappe.whitelist()
def pending_contracts(filters=None):
	return _card_payload("pending")


@frappe.whitelist()
def active_contracts(filters=None):
	return _card_payload("active")


@frappe.whitelist()
def terminated_contracts(filters=None):
	return _card_payload("terminated")


@frappe.whitelist()
def expired_contracts(filters=None):
	return _card_payload("expired")


@frappe.whitelist()
def completed_contracts(filters=None):
	return _card_payload("completed")


@frappe.whitelist()
def critical_contracts(filters=None):
	return _health_card_payload("critical")


@frappe.whitelist()
def attention_needed_contracts(filters=None):
	return _health_card_payload("attention")


@frappe.whitelist()
def healthy_contracts(filters=None):
	return _health_card_payload("healthy")
