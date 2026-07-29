import json

import frappe


DASHBOARD_BLOCK = "SF Contract Dashboard"

CONTRACT_NUMBER_CARDS = [
	{
		"name": "Total Contracts",
		"status": None,
		"method": "sf_contracts.contract_number_cards.total_contracts",
		"color": "#005aa8",
		"background_color": "#eaf4ff",
	},
	{
		"name": "Pending Contracts",
		"status": "Pending",
		"method": "sf_contracts.contract_number_cards.pending_contracts",
		"color": "#b76b00",
		"background_color": "#fff8e8",
	},
	{
		"name": "Active Contracts",
		"status": "Active",
		"method": "sf_contracts.contract_number_cards.active_contracts",
		"color": "#08763d",
		"background_color": "#edf9f2",
	},
	{
		"name": "Terminated Contracts",
		"status": "Terminated",
		"method": "sf_contracts.contract_number_cards.terminated_contracts",
		"color": "#b42318",
		"background_color": "#fff0f0",
	},
	{
		"name": "Expired Contracts",
		"status": "Expired",
		"method": "sf_contracts.contract_number_cards.expired_contracts",
		"color": "#b42318",
		"background_color": "#fff0f0",
	},
	{
		"name": "Completed Contracts",
		"status": "Completed",
		"method": "sf_contracts.contract_number_cards.completed_contracts",
		"color": "#005aa8",
		"background_color": "#eaf4ff",
	},
]


def get_dashboard_block_html():
	return """
<div class="sfw-contract-dashboard">
	<div class="sfw-hero">
		<div>
			<div class="sfw-eyebrow">SF Group of Companies Ltd</div>
			<div class="sfw-title">Contract Management Dashboard</div>
			<div class="sfw-subtitle">Track contract lifecycle, pending execution, expiry risk, and Legal action items.</div>
		</div>
		<button class="sfw-new-contract">New Contract</button>
	</div>
	<div class="sfw-cards"></div>
	<div class="sfw-expanded"></div>
	<div class="sfw-grid">
		<div class="sfw-panel">
			<div class="sfw-panel-title">Lifecycle Predictor</div>
			<div class="sfw-predictor"></div>
		</div>
		<div class="sfw-panel">
			<div class="sfw-panel-title">Contracts Near Expiration</div>
			<div data-watchlist="expiring_soon"></div>
		</div>
		<div class="sfw-panel">
			<div class="sfw-panel-title">Contracts Near Completion</div>
			<div data-watchlist="near_completion"></div>
		</div>
		<div class="sfw-panel">
			<div class="sfw-panel-title">Unsigned / Pending Contracts</div>
			<div data-watchlist="unsigned_pending"></div>
		</div>
	</div>
</div>
"""


def get_dashboard_block_style():
	return """
.sfw-contract-dashboard {
	--sf-blue: #005aa8;
	--sf-blue-dark: #003f7a;
	--sf-blue-soft: #eaf4ff;
	--sf-green: #009847;
	--sf-line: #d8e7f5;
	--sf-ink: #12314f;
	font-family: var(--font-stack);
}
.sfw-hero {
	align-items: center;
	background: linear-gradient(135deg, var(--sf-blue), var(--sf-blue-dark));
	border-radius: 8px;
	color: #fff;
	display: flex;
	justify-content: space-between;
	margin-bottom: 14px;
	overflow: hidden;
	padding: 22px 24px;
	position: relative;
}
.sfw-hero::after {
	background: radial-gradient(circle, rgba(255,255,255,.24) 0 2px, transparent 3px), radial-gradient(circle, rgba(0,152,71,.38) 0 4px, transparent 5px);
	background-size: 34px 34px, 58px 58px;
	content: "";
	height: 180px;
	opacity: .55;
	position: absolute;
	right: -34px;
	top: -42px;
	width: 250px;
}
.sfw-eyebrow {
	color: rgba(255,255,255,.82);
	font-size: 12px;
	font-weight: 700;
	letter-spacing: .08em;
	text-transform: uppercase;
}
.sfw-title {
	font-size: 26px;
	font-weight: 800;
	letter-spacing: 0;
	line-height: 1.15;
	margin-top: 4px;
}
.sfw-subtitle {
	color: rgba(255,255,255,.84);
	font-size: 13px;
	line-height: 1.45;
	margin-top: 6px;
	max-width: 680px;
}
.sfw-new-contract {
	background: #fff;
	border: 1px solid #fff;
	border-radius: 6px;
	color: var(--sf-blue);
	cursor: pointer;
	font-weight: 700;
	padding: 8px 12px;
	position: relative;
	z-index: 1;
}
.sfw-cards {
	display: grid;
	gap: 12px;
	grid-template-columns: repeat(auto-fit, minmax(175px, 1fr));
	margin-bottom: 12px;
}
.sfw-card {
	background: #fff;
	border: 1px solid var(--sf-line);
	border-radius: 8px;
	box-shadow: 0 8px 22px rgba(0,72,138,.08);
	cursor: pointer;
	display: grid;
	gap: 8px;
	grid-template-columns: 1fr auto;
	min-height: 92px;
	padding: 16px;
	position: relative;
	text-align: left;
}
.sfw-card::before {
	background: var(--sf-blue);
	border-radius: 8px 0 0 8px;
	content: "";
	height: 100%;
	left: 0;
	position: absolute;
	top: 0;
	width: 4px;
}
.sfw-card:hover,
.sfw-card.is-active {
	border-color: rgba(0,90,168,.38);
	box-shadow: 0 14px 34px rgba(0,72,138,.12);
}
.sfw-card-label {
	color: var(--sf-ink);
	font-size: 13px;
	font-weight: 700;
}
.sfw-card-count {
	font-size: 30px;
	font-weight: 800;
	line-height: 1;
}
.sfw-expanded {
	margin-bottom: 12px;
}
.sfw-grid {
	display: grid;
	gap: 12px;
	grid-template-columns: repeat(2, minmax(0, 1fr));
}
.sfw-panel {
	background: #fff;
	border: 1px solid var(--sf-line);
	border-radius: 8px;
	box-shadow: 0 8px 22px rgba(0,72,138,.07);
	padding: 16px;
}
.sfw-panel-header {
	align-items: center;
	display: flex;
	justify-content: space-between;
	margin-bottom: 12px;
}
.sfw-panel-title {
	color: var(--sf-blue-dark);
	font-size: 15px;
	font-weight: 800;
	margin-bottom: 10px;
}
.sfw-list {
	display: grid;
	gap: 8px;
}
.sfw-row {
	align-items: center;
	background: #f8fbff;
	border: 1px solid #edf4fb;
	border-radius: 8px;
	cursor: pointer;
	display: grid;
	gap: 10px;
	grid-template-columns: minmax(0, 1fr) auto;
	padding: 10px 12px;
	text-align: left;
	width: 100%;
}
.sfw-row:hover {
	background: #fff;
	border-color: rgba(0,90,168,.28);
}
.sfw-row strong,
.sfw-row span {
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}
.sfw-row-meta {
	display: grid;
	gap: 3px;
	justify-items: end;
}
.sfw-pill {
	border-radius: 999px;
	font-size: 12px;
	font-weight: 700;
	padding: 3px 8px;
}
.sfw-pill.green { background: #e7f7ee; color: #08763d; }
.sfw-pill.orange { background: #fff4df; color: #9a5b00; }
.sfw-pill.red { background: #ffe9e9; color: #b42318; }
.sfw-pill.blue { background: #eaf4ff; color: #005aa8; }
.sfw-pill.gray { background: #eef1f4; color: #4b5563; }
.sfw-predictor-row {
	align-items: center;
	border-bottom: 1px solid var(--sf-line);
	display: grid;
	gap: 8px;
	grid-template-columns: 1fr auto;
	min-height: 38px;
}
.sfw-predictor-row:last-child {
	border-bottom: 0;
}
.sfw-empty {
	background: var(--sf-blue-soft);
	border-radius: 8px;
	color: var(--sf-ink);
	padding: 12px;
}
.sfw-link {
	background: var(--sf-blue);
	border: 1px solid var(--sf-blue);
	border-radius: 6px;
	color: #fff;
	cursor: pointer;
	font-size: 12px;
	font-weight: 700;
	padding: 7px 10px;
}
.text-green { color: #08763d; }
.text-orange { color: #b76b00; }
.text-red { color: #b42318; }
.text-blue { color: #005aa8; }
.text-gray { color: #4b5563; }
@media (max-width: 991px) {
	.sfw-grid { grid-template-columns: 1fr; }
}
@media (max-width: 575px) {
	.sfw-hero,
	.sfw-row {
		align-items: flex-start;
		grid-template-columns: 1fr;
	}
	.sfw-hero {
		flex-direction: column;
	}
	.sfw-row-meta {
		justify-items: start;
	}
}
"""


def get_dashboard_block_script():
	return """
const $root = $(root_element);
let dashboardData = null;
let activeStatus = null;

function escapeHTML(value) {
	return frappe.utils.escape_html(value || "");
}

function render() {
	renderCards(dashboardData.cards || []);
	renderExpanded(activeStatus || (dashboardData.cards || [])[0]?.status);
	renderPredictor(dashboardData.predictor || []);
	renderWatchlists(dashboardData.watchlists || {});
}

function renderCards(cards) {
	const $cards = $root.find(".sfw-cards").empty();
	cards.forEach((card) => {
		const $card = $(`
			<button class="sfw-card ${card.status === activeStatus ? "is-active" : ""}" data-status="${escapeHTML(card.status)}">
				<span class="sfw-card-label">${escapeHTML(card.label)}</span>
				<span class="sfw-card-count text-${card.color || "gray"}">${card.count}</span>
			</button>
		`);
		$card.on("click", () => {
			activeStatus = activeStatus === card.status ? null : card.status;
			render();
		});
		$cards.append($card);
	});
}

function renderExpanded(status) {
	const card = (dashboardData.cards || []).find((item) => item.status === status);
	const $expanded = $root.find(".sfw-expanded").empty();
	if (!card) return;

	$expanded.html(`
		<div class="sfw-panel">
			<div class="sfw-panel-header">
				<div>
					<div class="sfw-panel-title">${escapeHTML(card.label)}</div>
					<div class="text-muted">Click a row to open the Contract record.</div>
				</div>
				<button class="sfw-link" data-view-all="${escapeHTML(card.status)}">View All</button>
			</div>
			<div class="sfw-list"></div>
		</div>
	`);
	$expanded.find("[data-view-all]").on("click", () => {
		frappe.route_options = { sf_contract_lifecycle_status: card.status };
		frappe.set_route("List", "Contract");
	});
	renderContractList($expanded.find(".sfw-list"), card.contracts || [], "No contracts found for this status.");
}

function renderPredictor(items) {
	const $predictor = $root.find(".sfw-predictor").empty();
	items.forEach((item) => {
		$predictor.append(`
			<div class="sfw-predictor-row">
				<span>${escapeHTML(item.label)}</span>
				<strong class="text-${item.indicator || "gray"}">${item.value}</strong>
			</div>
		`);
	});
}

function renderWatchlists(watchlists) {
	renderContractList($root.find('[data-watchlist="expiring_soon"]'), watchlists.expiring_soon || [], "No active contracts expiring in the next 90 days.", "days left");
	renderContractList($root.find('[data-watchlist="near_completion"]'), watchlists.near_completion || [], "No active contracts ending in the next 30 days.", "days left");
	renderContractList($root.find('[data-watchlist="unsigned_pending"]'), watchlists.unsigned_pending || [], "No unsigned pending contracts.", "days pending", true);
}

function renderContractList($target, contracts, emptyMessage, daysLabel, useDaysOpen) {
	$target.empty();
	if (!contracts.length) {
		$target.append(`<div class="sfw-empty">${escapeHTML(emptyMessage)}</div>`);
		return;
	}
	contracts.forEach((contract) => {
		const days = useDaysOpen ? contract.days_open : contract.days_to_end;
		const daysText = daysLabel && days !== null && days !== undefined ? `${days} ${daysLabel}` : "";
		const color = contract.status_color || "gray";
		const $row = $(`
			<button class="sfw-row" data-contract="${escapeHTML(contract.name)}">
				<span>
					<strong>${escapeHTML(contract.party || contract.name)}</strong>
					<span class="text-muted">${escapeHTML(contract.name)}</span>
				</span>
				<span class="sfw-row-meta">
					<span class="sfw-pill ${color}">${escapeHTML(contract.lifecycle_status)}</span>
					${daysText ? `<span>${escapeHTML(daysText)}</span>` : ""}
				</span>
			</button>
		`);
		$row.on("click", () => frappe.set_route("Form", "Contract", contract.name));
		$target.append($row);
	});
}

$root.find(".sfw-new-contract").on("click", () => frappe.new_doc("Contract"));

frappe.call({
	method: "sf_contracts.dashboard.get_contract_dashboard",
	callback(response) {
		dashboardData = response.message || {};
		render();
	},
});
"""


def create_contract_dashboard_block():
	if frappe.db.exists("Custom HTML Block", DASHBOARD_BLOCK):
		block = frappe.get_doc("Custom HTML Block", DASHBOARD_BLOCK)
	else:
		block = frappe.new_doc("Custom HTML Block")
		block.name = DASHBOARD_BLOCK

	block.html = get_dashboard_block_html()
	block.style = get_dashboard_block_style()
	block.script = get_dashboard_block_script()
	block.private = 0
	block.save(ignore_permissions=True)


def create_contract_number_cards():
	for card_config in CONTRACT_NUMBER_CARDS:
		if frappe.db.exists("Number Card", card_config["name"]):
			card = frappe.get_doc("Number Card", card_config["name"])
		else:
			card = frappe.new_doc("Number Card")
			card.name = card_config["name"]

		card.label = card_config["name"]
		card.type = "Custom"
		card.document_type = "Contract"
		card.method = card_config["method"]
		card.function = "Count"
		card.filters_json = "[]"
		card.is_public = 1
		card.is_standard = 1
		card.module = "SF Contracts"
		card.currency = ""
		card.show_percentage_stats = 0
		card.show_full_number = 1
		card.color = card_config["color"]
		card.background_color = card_config["background_color"]
		card.save(ignore_permissions=True)


def update_legal_workspace():
	workspace = frappe.get_doc("Workspace", "Legal")
	workspace.custom_blocks = []
	workspace.number_cards = []
	for card_config in CONTRACT_NUMBER_CARDS:
		workspace.append(
			"number_cards",
			{
				"number_card_name": card_config["name"],
				"label": card_config["name"],
			},
		)

	workspace.shortcuts = []
	for shortcut in [
		{
			"type": "DocType",
			"label": "Contract",
			"link_to": "Contract",
			"doc_view": "List",
			"icon": "file",
			"color": "#009847",
			"format": "{}",
			"stats_filter": "{}",
		},
		{
			"type": "DocType",
			"label": "Compliance Tracker",
			"link_to": "Contract Compliance Tracker",
			"doc_view": "List",
			"icon": "review",
			"color": "#005aa8",
			"format": "{}",
			"stats_filter": "{}",
		},
	]:
		workspace.append("shortcuts", shortcut)

	workspace.content = json.dumps(
		[
			{
				"id": "sfcm_header_dashboard",
				"type": "header",
				"data": {"text": '<span class="h4"><b>Contract Management Dashboard</b></span>', "col": 12},
			},
			{
				"id": "sfcm_total_contracts_card",
				"type": "number_card",
				"data": {"number_card_name": "Total Contracts", "col": 2},
			},
			{
				"id": "sfcm_pending_contracts_card",
				"type": "number_card",
				"data": {"number_card_name": "Pending Contracts", "col": 2},
			},
			{
				"id": "sfcm_active_contracts_card",
				"type": "number_card",
				"data": {"number_card_name": "Active Contracts", "col": 2},
			},
			{
				"id": "sfcm_terminated_contracts_card",
				"type": "number_card",
				"data": {"number_card_name": "Terminated Contracts", "col": 2},
			},
			{
				"id": "sfcm_expired_contracts_card",
				"type": "number_card",
				"data": {"number_card_name": "Expired Contracts", "col": 2},
			},
			{
				"id": "sfcm_completed_contracts_card",
				"type": "number_card",
				"data": {"number_card_name": "Completed Contracts", "col": 2},
			},
			{"id": "sfcm_spacer_1", "type": "spacer", "data": {"col": 12}},
			{
				"id": "sfcm_header_shortcuts",
				"type": "header",
				"data": {"text": '<span class="h4"><b>Shortcuts</b></span>', "col": 12},
			},
			{"id": "sfcm_contract_shortcut", "type": "shortcut", "data": {"shortcut_name": "Contract", "col": 3}},
			{
				"id": "sfcm_compliance_tracker_shortcut",
				"type": "shortcut",
				"data": {"shortcut_name": "Compliance Tracker", "col": 3},
			},
			{"id": "sfcm_spacer_2", "type": "spacer", "data": {"col": 12}},
			{
				"id": "sfcm_header_records",
				"type": "header",
				"data": {"text": '<span class="h4"><b>Records</b></span>', "col": 12},
			},
			{"id": "sfcm_card_records", "type": "card", "data": {"card_name": "Records", "col": 4}},
		]
	)

	workspace.save(ignore_permissions=True)


def setup_legal_workspace_dashboard():
	create_contract_dashboard_block()
	create_contract_number_cards()
	update_legal_workspace()
	frappe.clear_cache()
