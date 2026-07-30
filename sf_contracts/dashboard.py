import frappe
from frappe import _
from frappe.utils import add_days, date_diff, getdate, nowdate


STATE_ORDER = (
	"Draft",
	"Pending Execution",
	"Executed – Awaiting Commencement",
	"Active",
	"Expired – Services Continuing",
	"Closed",
	"Terminated",
)
STATE_COLORS = {
	"Draft": "gray",
	"Pending Execution": "orange",
	"Executed – Awaiting Commencement": "blue",
	"Active": "green",
	"Terminated": "red",
	"Expired – Services Continuing": "red",
	"Closed": "blue",
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
	lifecycle_status = contract.get("sf_contract_lifecycle_status") or "Draft"

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
		state = contract["lifecycle_status"] or "Draft"
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
	unsigned_pending = _get_contracts(
		filters={
			"sf_contract_lifecycle_status": "Pending Execution",
			"is_signed": 0,
		},
		order_by="creation asc",
		limit_page_length=12,
	)

	return {
		"expiring_soon": expiring_soon,
		"near_completion": near_completion,
		"unsigned_pending": unsigned_pending,
	}


def _build_predictor_summary(watchlists, cards):
	card_counts = {card["status"]: card["count"] for card in cards}
	unsigned_over_14_days = len(
		[contract for contract in watchlists["unsigned_pending"] if contract["days_open"] >= 14]
	)

	return [
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
			"label": "Unsigned pending over 14 days",
			"value": unsigned_over_14_days,
			"indicator": "red" if unsigned_over_14_days else "green",
		},
		{
			"label": "Expired contracts requiring action",
			"value": card_counts.get("Expired – Services Continuing", 0),
			"indicator": "red" if card_counts.get("Expired – Services Continuing", 0) else "green",
		},
	]


@frappe.whitelist()
def get_contract_dashboard():
	_require_contract_read_permission()

	cards = _build_state_cards()
	watchlists = _build_watchlists()

	return {
		"cards": cards,
		"watchlists": watchlists,
		"predictor": _build_predictor_summary(watchlists, cards),
		"generated_on": nowdate(),
	}
