import json

import frappe


DASHBOARD_BLOCK = "SF Legal Command Center"

CONTRACT_NUMBER_CARDS = [
	{
		"name": "Total Contracts",
		"status": None,
		"method": "sf_contracts.contract_number_cards.total_contracts",
		"color": "#005aa8",
		"background_color": "#eaf4ff",
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
		"label": "Expired Contracts",
		"status": "Expired",
		"method": "sf_contracts.contract_number_cards.expired_contracts",
		"color": "#b42318",
		"background_color": "#fff0f0",
	},
	{
		"name": "Critical Contracts",
		"status": "Critical",
		"method": "sf_contracts.contract_number_cards.critical_contracts",
		"color": "#b42318",
		"background_color": "#fff0f0",
	},
	{
		"name": "Attention Needed Contracts",
		"status": "Attention Needed",
		"method": "sf_contracts.contract_number_cards.attention_needed_contracts",
		"color": "#b76b00",
		"background_color": "#fff8e8",
	},
	{
		"name": "Healthy Contracts",
		"status": "Healthy",
		"method": "sf_contracts.contract_number_cards.healthy_contracts",
		"color": "#08763d",
		"background_color": "#edf9f2",
	},
]


def get_dashboard_block_html():
	return """
<div class="sfw-contract-dashboard">
	<div class="sfw-hero">
		<div>
			<div class="sfw-eyebrow">SF Group of Companies Ltd</div>
			<div class="sfw-title">Legal Contract Command Center</div>
			<div class="sfw-subtitle">Visual oversight for contract health, lifecycle movement, expiry risk, and urgent Legal actions.</div>
		</div>
		<button class="sfw-new-contract">New Contract</button>
	</div>
	<div class="sfw-visual-grid">
		<div class="sfw-panel sfw-panel-health">
			<div class="sfw-panel-title">Contract Health</div>
			<div class="sfw-health-visual"></div>
		</div>
		<div class="sfw-panel sfw-panel-compliance-pie">
			<div class="sfw-panel-title">Compliance Tracker</div>
			<div class="sfw-compliance-tracker-visual"></div>
		</div>
		<div class="sfw-panel sfw-panel-funnel">
			<div class="sfw-panel-title">Contract Life Cycle</div>
			<div class="sfw-lifecycle-funnel"></div>
		</div>
		<div class="sfw-panel sfw-panel-expiry">
			<div class="sfw-panel-title">Expiry Timeline</div>
			<div class="sfw-expiry-timeline"></div>
		</div>
		<div class="sfw-panel sfw-panel-actions">
			<div class="sfw-panel-title">Action Queue</div>
			<div data-watchlist="contract_health"></div>
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
.sfw-visual-grid {
	display: grid;
	gap: 12px;
	grid-template-columns: repeat(2, minmax(0, 1fr));
	margin-bottom: 12px;
}
.sfw-panel-health,
.sfw-panel-compliance-pie,
.sfw-panel-expiry {
	min-height: 280px;
}
.sfw-panel-funnel,
.sfw-panel-actions,
.sfw-panel-compliance,
.sfw-panel-expiring {
	min-height: 280px;
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
.sfw-health-visual,
.sfw-compliance-tracker-visual {
	align-items: center;
	display: grid;
	gap: 18px;
	grid-template-columns: auto minmax(0, 1fr);
	min-height: 220px;
}
.sfw-donut {
	align-items: center;
	background: conic-gradient(#eaecf0 0deg 360deg);
	border-radius: 50%;
	display: flex;
	height: 172px;
	justify-content: center;
	position: relative;
	width: 172px;
}
.sfw-donut::after {
	background: #fff;
	border-radius: 50%;
	content: "";
	height: 112px;
	position: absolute;
	width: 112px;
}
.sfw-donut-center {
	color: var(--sf-ink);
	display: grid;
	font-size: 12px;
	font-weight: 700;
	justify-items: center;
	position: relative;
	z-index: 1;
}
.sfw-donut-center strong {
	color: var(--sf-blue-dark);
	font-size: 28px;
	line-height: 1;
}
.sfw-legend {
	display: grid;
	gap: 10px;
}
.sfw-legend-row {
	align-items: center;
	background: transparent;
	border: 0;
	color: inherit;
	cursor: pointer;
	display: grid;
	gap: 8px;
	grid-template-columns: auto minmax(0, 1fr) auto;
	padding: 0;
	text-align: left;
	width: 100%;
}
.sfw-legend-row:hover span:nth-child(2) {
	color: var(--sf-blue);
}
.sfw-dot {
	border-radius: 50%;
	height: 10px;
	width: 10px;
}
.sfw-dot.green { background: #08763d; }
.sfw-dot.orange { background: #b76b00; }
.sfw-dot.red { background: #b42318; }
.sfw-dot.blue { background: #005aa8; }
.sfw-dot.gray { background: #4b5563; }
.sfw-funnel {
	display: grid;
	gap: 9px;
}
.sfw-funnel-row {
	background: transparent;
	border: 0;
	cursor: pointer;
	display: grid;
	gap: 6px;
	padding: 0;
	text-align: left;
	width: 100%;
}
.sfw-funnel-label {
	align-items: center;
	display: flex;
	justify-content: space-between;
}
.sfw-funnel-track {
	background: #eef4fb;
	border-radius: 999px;
	height: 14px;
	overflow: hidden;
}
.sfw-funnel-bar {
	border-radius: inherit;
	height: 100%;
	min-width: 8px;
	transition: width .25s ease;
}
.sfw-funnel-bar.green { background: #08763d; }
.sfw-funnel-bar.orange { background: #b76b00; }
.sfw-funnel-bar.red { background: #b42318; }
.sfw-funnel-bar.blue { background: #005aa8; }
.sfw-funnel-bar.gray { background: #667085; }
.sfw-expiry-timeline {
	display: grid;
	gap: 12px;
}
.sfw-expiry-band {
	background: #f8fbff;
	border: 1px solid #edf4fb;
	border-radius: 8px;
	padding: 10px 12px;
}
.sfw-expiry-band-head {
	align-items: center;
	display: flex;
	justify-content: space-between;
	margin-bottom: 8px;
}
.sfw-expiry-track {
	background: #e8eef6;
	border-radius: 999px;
	height: 10px;
	overflow: hidden;
}
.sfw-expiry-fill {
	border-radius: inherit;
	height: 100%;
	min-width: 5px;
}
.sfw-expiry-fill.green { background: #08763d; }
.sfw-expiry-fill.orange { background: #b76b00; }
.sfw-expiry-fill.red { background: #b42318; }
.sfw-expiry-fill.blue { background: #005aa8; }
.sfw-expiry-fill.gray { background: #667085; }
.sfw-heatmap {
	display: grid;
	gap: 8px;
}
.sfw-heatmap-row {
	align-items: center;
	background: #f8fbff;
	border: 1px solid #edf4fb;
	border-radius: 8px;
	cursor: pointer;
	display: grid;
	gap: 10px;
	grid-template-columns: minmax(0, 1.2fr) minmax(0, .9fr) auto;
	padding: 10px 12px;
	text-align: left;
	width: 100%;
}
.sfw-heatmap-row:hover {
	background: #fff;
	border-color: rgba(0,90,168,.28);
}
.sfw-heatmap-main,
.sfw-heatmap-meta {
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}
.sfw-heatmap-score {
	border-radius: 999px;
	font-size: 12px;
	font-weight: 800;
	min-width: 54px;
	padding: 4px 8px;
	text-align: center;
}
.sfw-heatmap-score.green { background: #e7f7ee; color: #08763d; }
.sfw-heatmap-score.orange { background: #fff4df; color: #9a5b00; }
.sfw-heatmap-score.red { background: #ffe9e9; color: #b42318; }
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
	.sfw-visual-grid,
	.sfw-grid { grid-template-columns: 1fr; }
}
@media (max-width: 575px) {
	.sfw-hero,
	.sfw-row,
	.sfw-health-visual {
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
	return frappe.utils.escape_html(String(value ?? ""));
}

function render() {
	renderVisualizations(dashboardData.visualizations || {});
	renderWatchlists(dashboardData.watchlists || {});
}

function renderVisualizations(visualizations) {
	renderDonut(".sfw-health-visual", visualizations.health_distribution || [], "Total", "Contract");
	renderDonut(".sfw-compliance-tracker-visual", visualizations.compliance_tracker_distribution || [], "Trackers", "Contract Compliance Tracker");
	renderLifecycleFunnel(visualizations.lifecycle_distribution || []);
	renderExpiryTimeline(visualizations.expiry_buckets || []);
}

function getVisualColor(color) {
	return {
		green: "#08763d",
		orange: "#b76b00",
		red: "#b42318",
		blue: "#005aa8",
		gray: "#667085",
	}[color || "gray"] || "#667085";
}

function renderDonut(selector, items, totalLabel, routeDoctype) {
	const $target = $root.find(selector).empty();
	const total = items.reduce((sum, item) => sum + cint(item.count), 0);
	let angle = 0;
	const segments = [];

	items.forEach((item) => {
		const degrees = total ? (cint(item.count) / total) * 360 : 0;
		segments.push(`${getVisualColor(item.color)} ${angle}deg ${angle + degrees}deg`);
		angle += degrees;
	});

	const background = segments.length && total ? `conic-gradient(${segments.join(", ")})` : "";
	const $donut = $(`
		<div class="sfw-donut" style="${background ? `background:${background}` : ""}">
			<div class="sfw-donut-center">
				<strong>${total}</strong>
				<span>${escapeHTML(totalLabel)}</span>
			</div>
		</div>
	`);
	const $legend = $('<div class="sfw-legend"></div>');

	items.forEach((item) => {
		const $row = $(`
			<button class="sfw-legend-row" data-label="${escapeHTML(item.label)}">
				<span class="sfw-dot ${item.color || "gray"}"></span>
				<span>${escapeHTML(item.label)}</span>
				<strong class="text-${item.color || "gray"}">${cint(item.count)}</strong>
			</button>
		`);
		$row.on("click", () => openDonutSegment(routeDoctype, item));
		$legend.append($row);
	});

	$target.append($donut, $legend);
}

function openDonutSegment(routeDoctype, item) {
	if (!item.count) return;

	if (routeDoctype === "Contract") {
		frappe.route_options = item.route_options || { sf_contract_lifecycle_status: ["=", item.label] };
		frappe.set_route("List", "Contract");
		return;
	}

	frappe.route_options = item.route_options || {};
	frappe.set_route("List", routeDoctype);
}

function renderLifecycleFunnel(items) {
	const $target = $root.find(".sfw-lifecycle-funnel").empty();
	const maxCount = Math.max(...items.map((item) => cint(item.count)), 1);

	items.forEach((item) => {
		const width = Math.max((cint(item.count) / maxCount) * 100, item.count ? 8 : 0);
		const $row = $(`
			<button class="sfw-funnel-row" data-status="${escapeHTML(item.status)}">
				<span class="sfw-funnel-label">
					<span>${escapeHTML(item.label)}</span>
					<strong class="text-${item.color || "gray"}">${cint(item.count)}</strong>
				</span>
				<span class="sfw-funnel-track">
					<span class="sfw-funnel-bar ${item.color || "gray"}" style="width:${width}%"></span>
				</span>
			</button>
		`);
		$row.on("click", () => {
			frappe.route_options = { sf_contract_lifecycle_status: item.status };
			frappe.set_route("List", "Contract");
		});
		$target.append($row);
	});
}

function renderExpiryTimeline(items) {
	const $target = $root.find(".sfw-expiry-timeline").empty();
	const maxCount = Math.max(...items.map((item) => cint(item.count)), 1);

	items.forEach((item) => {
		const width = Math.max((cint(item.count) / maxCount) * 100, item.count ? 8 : 0);
		$target.append(`
			<div class="sfw-expiry-band">
				<div class="sfw-expiry-band-head">
					<div>
						<strong>${escapeHTML(item.label)}</strong>
						<div class="text-muted">${escapeHTML(item.range)}</div>
					</div>
					<strong class="text-${item.color || "gray"}">${cint(item.count)}</strong>
				</div>
				<div class="sfw-expiry-track">
					<div class="sfw-expiry-fill ${item.color || "gray"}" style="width:${width}%"></div>
				</div>
			</div>
		`);
	});
}

function renderComplianceHeatmap(items) {
	const $target = $root.find(".sfw-compliance-heatmap").empty();
	const $list = $('<div class="sfw-heatmap"></div>');

	if (!items.length) {
		$target.html(`<div class="sfw-empty">No compliance tracker records found.</div>`);
		return;
	}

	items.forEach((item) => {
		const $row = $(`
			<button class="sfw-heatmap-row" data-tracker="${escapeHTML(item.name)}">
				<span class="sfw-heatmap-main">
					<strong>${escapeHTML(item.party_name)}</strong>
					<span class="text-muted">${escapeHTML(item.contract)}</span>
				</span>
				<span class="sfw-heatmap-meta">${escapeHTML(item.contract_type)}</span>
				<span class="sfw-heatmap-score ${item.color || "gray"}">${cint(item.percentage)}%</span>
			</button>
		`);
		$row.on("click", () => frappe.set_route("Form", "Contract Compliance Tracker", item.name));
		$list.append($row);
	});

	$target.append($list);
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
	renderContractList($root.find('[data-watchlist="contract_health"]'), watchlists.contract_health || [], "No critical contracts.", null, false, true);
}

function renderContractList($target, contracts, emptyMessage, daysLabel, useDaysOpen, showHealthReason) {
	$target.empty();
	if (!contracts.length) {
		$target.append(`<div class="sfw-empty">${escapeHTML(emptyMessage)}</div>`);
		return;
	}
	contracts.forEach((contract) => {
		const days = useDaysOpen ? contract.days_open : contract.days_to_end;
		const daysText = daysLabel && days !== null && days !== undefined ? `${days} ${daysLabel}` : "";
		const color = showHealthReason ? contract.health_color || "gray" : contract.status_color || "gray";
		const pillText = showHealthReason ? contract.health_score || "Attention Needed" : contract.lifecycle_status;
		const reasonText = showHealthReason ? contract.health_reason || "" : "";
		const $row = $(`
			<button class="sfw-row" data-contract="${escapeHTML(contract.name)}">
				<span>
					<strong>${escapeHTML(contract.party || contract.name)}</strong>
					<span class="text-muted">${escapeHTML(reasonText || contract.name)}</span>
				</span>
				<span class="sfw-row-meta">
					<span class="sfw-pill ${color}">${escapeHTML(pillText)}</span>
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

		card.label = card_config.get("label") or card_config["name"]
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
	workspace.append(
		"custom_blocks",
		{
			"custom_block_name": DASHBOARD_BLOCK,
			"label": "Contract Management Dashboard",
		},
	)
	workspace.number_cards = []
	workspace.links = []
	for link in [
		{
			"type": "Card Break",
			"label": "Records",
			"onboard": 0,
		},
		{
			"type": "Link",
			"label": "Contract",
			"link_type": "DocType",
			"link_to": "Contract",
			"onboard": 1,
		},
		{
			"type": "Link",
			"label": "Contract Compliance Tracker",
			"link_type": "DocType",
			"link_to": "Contract Compliance Tracker",
			"onboard": 1,
		},
		{
			"type": "Link",
			"label": "Compliance Register",
			"link_type": "DocType",
			"link_to": "Compliance Register",
			"onboard": 1,
		},
		{
			"type": "Link",
			"label": "Compliance Category",
			"link_type": "DocType",
			"link_to": "Compliance Category",
			"onboard": 0,
		},
		{
			"type": "Link",
			"label": "Compliance Settings",
			"link_type": "DocType",
			"link_to": "Compliance Settings",
			"onboard": 0,
		},
		{
			"type": "Link",
			"label": "SF Companies",
			"link_type": "DocType",
			"link_to": "SF Companies",
			"onboard": 1,
		},
		{
			"type": "Link",
			"label": "Contract Template",
			"link_type": "DocType",
			"link_to": "Contract Template",
			"onboard": 0,
		},
		{
			"type": "Card Break",
			"label": "Reports",
			"onboard": 0,
		},
		{
			"type": "Link",
			"label": "Contract Management Report",
			"link_type": "Report",
			"link_to": "Contract Management Report",
			"is_query_report": 1,
			"onboard": 0,
		},
		{
			"type": "Link",
			"label": "Compliance by Company Report",
			"link_type": "Report",
			"link_to": "Compliance by Company Report",
			"is_query_report": 1,
			"onboard": 0,
		},
	]:
		workspace.append("links", link)

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
		{
			"type": "DocType",
			"label": "Compliance Register",
			"link_to": "Compliance Register",
			"doc_view": "List",
			"icon": "check-circle",
			"color": "#005aa8",
			"format": "{}",
			"stats_filter": "{}",
		},
		{
			"type": "DocType",
			"label": "SF Companies",
			"link_to": "SF Companies",
			"doc_view": "List",
			"icon": "organization",
			"color": "#009847",
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
				"id": "sfcm_custom_dashboard",
				"type": "custom_block",
				"data": {"custom_block_name": DASHBOARD_BLOCK, "col": 12},
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
			{
				"id": "sfcm_compliance_register_shortcut",
				"type": "shortcut",
				"data": {"shortcut_name": "Compliance Register", "col": 3},
			},
			{
				"id": "sfcm_sf_companies_shortcut",
				"type": "shortcut",
				"data": {"shortcut_name": "SF Companies", "col": 3},
			},
			{"id": "sfcm_spacer_2", "type": "spacer", "data": {"col": 12}},
			{
				"id": "sfcm_header_records",
				"type": "header",
				"data": {"text": '<span class="h4"><b>Records</b></span>', "col": 12},
			},
			{"id": "sfcm_card_records", "type": "card", "data": {"card_name": "Records", "col": 4}},
			{
				"id": "sfcm_header_reports",
				"type": "header",
				"data": {"text": '<span class="h4"><b>Reports</b></span>', "col": 12},
			},
			{"id": "sfcm_card_reports", "type": "card", "data": {"card_name": "Reports", "col": 4}},
		]
	)

	workspace.save(ignore_permissions=True)


def setup_legal_workspace_dashboard():
	create_contract_dashboard_block()
	create_contract_number_cards()
	update_legal_workspace()
	frappe.clear_cache()
