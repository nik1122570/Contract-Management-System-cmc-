import frappe
from frappe import _
from frappe.utils import add_days, date_diff, getdate, nowdate


STATE_ORDER = (
	"Active",
	"Expired",
	"Terminated",
)
STATE_COLORS = {
	"Active": "green",
	"Terminated": "red",
	"Expired": "red",
}
HEALTH_COLORS = {
	"Healthy": "green",
	"Attention Needed": "orange",
	"Critical": "red",
}
COMPLIANCE_TRACKER_COLORS = {
	"Compliant": "green",
	"Attention Needed": "orange",
	"Critical": "red",
	"Not Evaluated": "gray",
}


def _require_contract_read_permission():
	if not frappe.has_permission("Contract", "read"):
		frappe.throw(_("Not permitted to read Contract records."), frappe.PermissionError)


def _contract_fields():
	return [
		"name",
		"party_type",
		"party_name",
		"start_date",
		"end_date",
		"is_signed",
		"signed_on",
		"status",
		"sf_contract_lifecycle_status",
		"sf_signed_contract_document",
		"sf_completion_date",
		"sf_termination_date",
		"sf_contract_health_score",
		"sf_contract_health_reason",
		"modified",
		"creation",
	]


def _days_until(date_value):
	if not date_value:
		return None

	return date_diff(getdate(date_value), getdate(nowdate()))


def _days_open(creation):
	return max(date_diff(getdate(nowdate()), getdate(creation)), 0)


def _serialize_contract(contract):
	lifecycle_status = normalize_lifecycle_status(contract.get("sf_contract_lifecycle_status"))

	return {
		"name": contract.name,
		"party": contract.party_name,
		"party_type": contract.party_type,
		"start_date": contract.start_date,
		"end_date": contract.end_date,
		"is_signed": contract.is_signed,
		"signed_on": contract.signed_on,
		"lifecycle_status": lifecycle_status,
		"status_color": STATE_COLORS.get(lifecycle_status, "gray"),
		"signed_document": contract.get("sf_signed_contract_document"),
		"completion_date": contract.get("sf_completion_date"),
		"termination_date": contract.get("sf_termination_date"),
		"health_score": contract.get("sf_contract_health_score") or "Attention Needed",
		"health_reason": contract.get("sf_contract_health_reason"),
		"health_color": HEALTH_COLORS.get(contract.get("sf_contract_health_score"), "orange"),
		"days_to_end": _days_until(contract.end_date),
		"days_open": _days_open(contract.creation),
		"modified": contract.modified,
	}


def _get_contracts(filters=None, order_by="modified desc", limit_page_length=20):
	return [
		_serialize_contract(contract)
		for contract in frappe.get_list(
			"Contract",
			fields=_contract_fields(),
			filters=filters or {},
			order_by=order_by,
			limit_page_length=limit_page_length,
		)
	]


def _build_state_cards():
	all_contracts = _get_contracts(limit_page_length=500)
	contracts_by_state = {state: [] for state in STATE_ORDER}

	for contract in all_contracts:
		state = normalize_lifecycle_status(contract["lifecycle_status"])
		contracts_by_state.setdefault(state, []).append(contract)

	return [
		{
			"status": state,
			"label": f"{state} Contracts",
			"count": len(contracts_by_state.get(state, [])),
			"color": STATE_COLORS.get(state, "gray"),
			"contracts": contracts_by_state.get(state, [])[:12],
		}
		for state in STATE_ORDER
	]


def _build_health_distribution():
	return [
		{
			"label": state,
			"count": frappe.db.count("Contract", {"sf_contract_lifecycle_status": state}),
			"color": STATE_COLORS.get(state, "gray"),
			"route_options": {"sf_contract_lifecycle_status": ["=", state]},
		}
		for state in STATE_ORDER
	]


def _build_compliance_tracker_distribution():
	if not frappe.has_permission("Contract Compliance Tracker", "read"):
		return []

	distribution = {
		"Critical": 0,
		"Attention Needed": 0,
		"Compliant": 0,
		"Not Evaluated": 0,
	}
	trackers = frappe.get_list(
		"Contract Compliance Tracker",
		fields=["name", "compliance_percentage"],
		limit_page_length=500,
	)

	for tracker in trackers:
		if tracker.compliance_percentage is None:
			distribution["Not Evaluated"] += 1
			continue

		percentage = float(tracker.compliance_percentage or 0)
		if percentage >= 100:
			distribution["Compliant"] += 1
		elif percentage >= 70:
			distribution["Attention Needed"] += 1
		else:
			distribution["Critical"] += 1

	return [
		{
			"label": label,
			"count": count,
			"color": COMPLIANCE_TRACKER_COLORS.get(label, "gray"),
			"route_options": _get_compliance_tracker_route_options(label),
		}
		for label, count in distribution.items()
	]


def _get_compliance_tracker_route_options(label):
	if label == "Compliant":
		return {"compliance_percentage": [">=", 100]}
	if label == "Attention Needed":
		return {"compliance_percentage": ["between", [70, 99.99]]}
	if label == "Critical":
		return {"compliance_percentage": ["<", 70]}
	if label == "Not Evaluated":
		return {"compliance_percentage": ["is", "not set"]}

	return {}


def _build_lifecycle_distribution(cards):
	total = sum(card["count"] for card in cards) or 1
	return [
		{
			"status": card["status"],
			"label": card["status"],
			"count": card["count"],
			"color": card["color"],
			"percentage": round((card["count"] / total) * 100),
		}
		for card in cards
	]


def _build_expiry_buckets():
	today = getdate(nowdate())
	buckets = {
		"Expired": {"label": "Expired", "count": 0, "color": "red", "range": "Past end date"},
		"0-30": {"label": "0-30 Days", "count": 0, "color": "red", "range": "Immediate action"},
		"31-60": {"label": "31-60 Days", "count": 0, "color": "orange", "range": "Prepare renewal"},
		"61-90": {"label": "61-90 Days", "count": 0, "color": "blue", "range": "Upcoming"},
	}
	contracts = frappe.get_list(
		"Contract",
		fields=["name", "end_date", "sf_contract_lifecycle_status"],
		filters={"end_date": ["is", "set"]},
		limit_page_length=500,
	)

	for contract in contracts:
		if normalize_lifecycle_status(contract.get("sf_contract_lifecycle_status")) == "Terminated":
			continue

		days = date_diff(getdate(contract.end_date), today)

		if days < 0:
			buckets["Expired"]["count"] += 1
		elif days <= 30:
			buckets["0-30"]["count"] += 1
		elif days <= 60:
			buckets["31-60"]["count"] += 1
		elif days <= 90:
			buckets["61-90"]["count"] += 1

	return list(buckets.values())


def _build_compliance_heatmap():
	rows = []
	trackers = frappe.get_list(
		"Contract Compliance Tracker",
		fields=[
			"name",
			"contract",
			"contractor",
			"contract_type",
			"compliance_percentage",
		],
		order_by="modified desc",
		limit_page_length=12,
	)

	for tracker in trackers:
		percentage = round(float(tracker.compliance_percentage or 0))
		if percentage >= 90:
			color = "green"
		elif percentage >= 70:
			color = "orange"
		else:
			color = "red"

		rows.append(
			{
				"name": tracker.name,
				"contract": tracker.contract,
				"contractor": tracker.contractor or "Not Set",
				"contract_type": tracker.contract_type or "Not Set",
				"percentage": percentage,
				"color": color,
			}
		)

	return rows


def _build_visualizations(cards):
	return {
		"health_distribution": _build_health_distribution(),
		"compliance_tracker_distribution": _build_compliance_tracker_distribution(),
		"lifecycle_distribution": _build_lifecycle_distribution(cards),
		"expiry_buckets": _build_expiry_buckets(),
		"compliance_heatmap": _build_compliance_heatmap(),
	}


def _build_watchlists():
	today = getdate(nowdate())
	expiry_cutoff = add_days(today, 90)
	completion_cutoff = add_days(today, 30)

	expiring_soon = _get_contracts(
		filters={
			"sf_contract_lifecycle_status": "Active",
			"end_date": ["between", [today, expiry_cutoff]],
		},
		order_by="end_date asc",
		limit_page_length=12,
	)
	near_completion = _get_contracts(
		filters={
			"sf_contract_lifecycle_status": "Active",
			"end_date": ["between", [today, completion_cutoff]],
		},
		order_by="end_date asc",
		limit_page_length=12,
	)
	contract_health = _get_contracts(
		filters={"sf_contract_health_score": "Critical"},
		order_by="modified desc",
		limit_page_length=12,
	)

	return {
		"contract_health": contract_health,
		"expiring_soon": expiring_soon,
		"near_completion": near_completion,
	}


def _build_predictor_summary(watchlists, cards):
	card_counts = {card["status"]: card["count"] for card in cards}

	return [
		{
			"label": "Critical contracts",
			"value": frappe.db.count("Contract", {"sf_contract_health_score": "Critical"}),
			"indicator": "red"
			if frappe.db.count("Contract", {"sf_contract_health_score": "Critical"})
			else "green",
		},
		{
			"label": "Contracts expiring in 90 days",
			"value": len(watchlists["expiring_soon"]),
			"indicator": "orange" if watchlists["expiring_soon"] else "green",
		},
		{
			"label": "Contracts ending in 30 days",
			"value": len(watchlists["near_completion"]),
			"indicator": "red" if watchlists["near_completion"] else "green",
		},
		{
			"label": "Expired contracts requiring action",
			"value": card_counts.get("Expired", 0),
			"indicator": "red" if card_counts.get("Expired", 0) else "green",
		},
	]


def normalize_lifecycle_status(status):
	if status in ("Terminated",):
		return "Terminated"
	if status in ("Expired", "Expired – Services Continuing", "Expired â€“ Services Continuing"):
		return "Expired"
	return "Active"


@frappe.whitelist()
def get_contract_dashboard():
	_require_contract_read_permission()

	cards = _build_state_cards()
	watchlists = _build_watchlists()

	return {
		"cards": cards,
		"watchlists": watchlists,
		"predictor": _build_predictor_summary(watchlists, cards),
		"visualizations": _build_visualizations(cards),
		"generated_on": nowdate(),
	}
