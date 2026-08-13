(function () {
	const DASHBOARD_ID = "sf-legal-command-center";

	const colors = {
		green: "#08763d",
		orange: "#b76b00",
		red: "#b42318",
		blue: "#005aa8",
		gray: "#667085",
	};

	frappe.router.on("change", () => {
		setTimeout(render_legal_workspace_dashboard, 450);
	});

	$(document).on("workspace_refresh", () => {
		setTimeout(render_legal_workspace_dashboard, 450);
	});

	$(document).ready(() => {
		setTimeout(render_legal_workspace_dashboard, 900);
	});

	function is_legal_workspace() {
		const route = (frappe.get_route() || []).map((part) => String(part).toLowerCase());
		const title = $(".page-title .title-text, .page-title").first().text().trim().toLowerCase();

		return route.includes("legal") || title === "legal";
	}

	function render_legal_workspace_dashboard() {
		if (!is_legal_workspace()) {
			$(`#${DASHBOARD_ID}`).remove();
			return;
		}

		const $target = get_workspace_target();
		if (!$target.length || $(`#${DASHBOARD_ID}`).length) {
			return;
		}

		inject_styles();
		$target.prepend(get_shell_html());

		frappe.call({
			method: "sf_contracts.dashboard.get_contract_dashboard",
			callback(response) {
				const data = response.message || {};
				render_visuals(data);
			},
		});
	}

	function get_workspace_target() {
		const selectors = [
			".layout-main-section .workspace-body",
			".layout-main-section .workspace-content",
			".layout-main-section",
		];

		for (const selector of selectors) {
			const $target = $(selector).first();
			if ($target.length) {
				return $target;
			}
		}

		return $();
	}

	function escape_html(value) {
		return frappe.utils.escape_html(String(value ?? ""));
	}

	function get_shell_html() {
		return `
			<div id="${DASHBOARD_ID}" class="sfw-contract-dashboard">
				<div class="sfw-hero">
					<div>
						<div class="sfw-eyebrow">SF Group of Companies Ltd</div>
						<div class="sfw-title">Legal Contract Command Center</div>
						<div class="sfw-subtitle">Visual oversight for contract health, lifecycle movement, expiry risk, and urgent Legal actions.</div>
					</div>
					<button class="sfw-new-contract">New Contract</button>
				</div>

				<div class="sfw-visual-grid">
					<div class="sfw-panel">
						<div class="sfw-panel-title">Contract Health</div>
						<div class="sfw-health-visual"></div>
					</div>
					<div class="sfw-panel">
						<div class="sfw-panel-title">Compliance Tracker</div>
						<div class="sfw-compliance-tracker-visual"></div>
					</div>
					<div class="sfw-panel">
						<div class="sfw-panel-title">Lifecycle Funnel</div>
						<div class="sfw-lifecycle-funnel"></div>
					</div>
					<div class="sfw-panel">
						<div class="sfw-panel-title">Expiry Timeline</div>
						<div class="sfw-expiry-timeline"></div>
					</div>
					<div class="sfw-panel">
						<div class="sfw-panel-title">Action Queue</div>
						<div data-watchlist="contract_health"></div>
					</div>
				</div>

				<div class="sfw-grid">
					<div class="sfw-panel">
						<div class="sfw-panel-title">Unsigned / Pending Contracts</div>
						<div data-watchlist="unsigned_pending"></div>
					</div>
				</div>
			</div>
		`;
	}

	function render_visuals(data) {
		const visualizations = data.visualizations || {};
		render_donut(".sfw-health-visual", visualizations.health_distribution || [], "Total", "Contract");
		render_donut(
			".sfw-compliance-tracker-visual",
			visualizations.compliance_tracker_distribution || [],
			"Trackers",
			"Contract Compliance Tracker"
		);
		render_lifecycle_funnel(visualizations.lifecycle_distribution || []);
		render_expiry_timeline(visualizations.expiry_buckets || []);
		render_contract_list(
			$('[data-watchlist="contract_health"]'),
			(data.watchlists || {}).contract_health || [],
			"No critical contracts.",
			null,
			false,
			true
		);
		render_contract_list(
			$('[data-watchlist="unsigned_pending"]'),
			(data.watchlists || {}).unsigned_pending || [],
			"No unsigned pending contracts.",
			"days pending",
			true
		);

		$(`#${DASHBOARD_ID} .sfw-new-contract`).on("click", () => frappe.new_doc("Contract"));
	}

	function render_donut(selector, items, total_label, route_doctype) {
		const $target = $(`#${DASHBOARD_ID} ${selector}`).empty();
		const total = items.reduce((sum, item) => sum + cint(item.count), 0);
		let angle = 0;
		const segments = [];

		items.forEach((item) => {
			const degrees = total ? (cint(item.count) / total) * 360 : 0;
			segments.push(`${colors[item.color] || colors.gray} ${angle}deg ${angle + degrees}deg`);
			angle += degrees;
		});

		const background = segments.length && total ? `background: conic-gradient(${segments.join(", ")});` : "";
		const $legend = $('<div class="sfw-legend"></div>');

		items.forEach((item) => {
			const $row = $(`
				<button class="sfw-legend-row">
					<span class="sfw-dot ${item.color || "gray"}"></span>
					<span>${escape_html(item.label)}</span>
					<strong class="text-${item.color || "gray"}">${cint(item.count)}</strong>
				</button>
			`);
			$row.on("click", () => open_donut_segment(route_doctype, item));
			$legend.append($row);
		});

		$target.append(`
			<div class="sfw-donut" style="${background}">
				<div class="sfw-donut-center"><strong>${total}</strong><span>${escape_html(total_label)}</span></div>
			</div>
		`);
		$target.append($legend);
	}

	function open_donut_segment(route_doctype, item) {
		if (!item.count) {
			return;
		}

		if (route_doctype === "Contract") {
			frappe.route_options = { sf_contract_health_score: item.label };
			frappe.set_route("List", "Contract");
			return;
		}

		frappe.route_options = item.route_options || {};
		frappe.set_route("List", route_doctype);
	}

	function render_lifecycle_funnel(items) {
		const $target = $(`#${DASHBOARD_ID} .sfw-lifecycle-funnel`).empty();
		const max_count = Math.max(...items.map((item) => cint(item.count)), 1);

		items.forEach((item) => {
			const width = Math.max((cint(item.count) / max_count) * 100, item.count ? 8 : 0);
			const $row = $(`
				<button class="sfw-funnel-row" data-status="${escape_html(item.status)}">
					<span class="sfw-funnel-label">
						<span>${escape_html(item.label)}</span>
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

	function render_expiry_timeline(items) {
		const $target = $(`#${DASHBOARD_ID} .sfw-expiry-timeline`).empty();
		const max_count = Math.max(...items.map((item) => cint(item.count)), 1);

		items.forEach((item) => {
			const width = Math.max((cint(item.count) / max_count) * 100, item.count ? 8 : 0);
			$target.append(`
				<div class="sfw-expiry-band">
					<div class="sfw-expiry-band-head">
						<div><strong>${escape_html(item.label)}</strong><div class="text-muted">${escape_html(item.range)}</div></div>
						<strong class="text-${item.color || "gray"}">${cint(item.count)}</strong>
					</div>
					<div class="sfw-expiry-track">
						<div class="sfw-expiry-fill ${item.color || "gray"}" style="width:${width}%"></div>
					</div>
				</div>
			`);
		});
	}

	function render_compliance_heatmap(items) {
		const $target = $(`#${DASHBOARD_ID} .sfw-compliance-heatmap`).empty();

		if (!items.length) {
			$target.html('<div class="sfw-empty">No compliance tracker records found.</div>');
			return;
		}

		items.forEach((item) => {
			const $row = $(`
				<button class="sfw-heatmap-row" data-tracker="${escape_html(item.name)}">
					<span class="sfw-heatmap-main">
						<strong>${escape_html(item.contractor)}</strong>
						<span class="text-muted">${escape_html(item.contract)}</span>
					</span>
					<span class="sfw-heatmap-meta">${escape_html(item.contract_type)}</span>
					<span class="sfw-heatmap-score ${item.color || "gray"}">${cint(item.percentage)}%</span>
				</button>
			`);
			$row.on("click", () => frappe.set_route("Form", "Contract Compliance Tracker", item.name));
			$target.append($row);
		});
	}

	function render_predictor(items) {
		const $target = $(`#${DASHBOARD_ID} .sfw-predictor`).empty();
		items.forEach((item) => {
			$target.append(`
				<div class="sfw-predictor-row">
					<span>${escape_html(item.label)}</span>
					<strong class="text-${item.indicator || "gray"}">${cint(item.value)}</strong>
				</div>
			`);
		});
	}

	function render_contract_list($target, contracts, empty_message, days_label, use_days_open, show_health_reason) {
		$target.empty();
		if (!contracts.length) {
			$target.append(`<div class="sfw-empty">${escape_html(empty_message)}</div>`);
			return;
		}

		contracts.forEach((contract) => {
			const days = use_days_open ? contract.days_open : contract.days_to_end;
			const days_text = days_label && days !== null && days !== undefined ? `${days} ${days_label}` : "";
			const color = show_health_reason ? contract.health_color || "gray" : contract.status_color || "gray";
			const pill_text = show_health_reason
				? contract.health_score || "Attention Needed"
				: contract.lifecycle_status;
			const reason_text = show_health_reason ? contract.health_reason || "" : "";
			const $row = $(`
				<button class="sfw-row" data-contract="${escape_html(contract.name)}">
					<span>
						<strong>${escape_html(contract.party || contract.name)}</strong>
						<span class="text-muted">${escape_html(reason_text || contract.name)}</span>
					</span>
					<span class="sfw-row-meta">
						<span class="sfw-pill ${color}">${escape_html(pill_text)}</span>
						${days_text ? `<span>${escape_html(days_text)}</span>` : ""}
					</span>
				</button>
			`);
			$row.on("click", () => frappe.set_route("Form", "Contract", contract.name));
			$target.append($row);
		});
	}

	function inject_styles() {
		if (document.getElementById("sf-legal-command-center-styles")) {
			return;
		}

		const style = document.createElement("style");
		style.id = "sf-legal-command-center-styles";
		style.textContent = `
			#${DASHBOARD_ID} {
				--sf-blue: #005aa8;
				--sf-blue-dark: #003f7a;
				--sf-blue-soft: #eaf4ff;
				--sf-line: #d8e7f5;
				--sf-ink: #12314f;
				margin-bottom: 24px;
			}
			#${DASHBOARD_ID} .sfw-hero {
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
			#${DASHBOARD_ID} .sfw-eyebrow { color: rgba(255,255,255,.82); font-size: 12px; font-weight: 700; text-transform: uppercase; }
			#${DASHBOARD_ID} .sfw-title { font-size: 26px; font-weight: 800; line-height: 1.15; margin-top: 4px; }
			#${DASHBOARD_ID} .sfw-subtitle { color: rgba(255,255,255,.84); font-size: 13px; margin-top: 6px; max-width: 760px; }
			#${DASHBOARD_ID} .sfw-new-contract { background: #fff; border: 1px solid #fff; border-radius: 6px; color: var(--sf-blue); cursor: pointer; font-weight: 700; padding: 8px 12px; }
			#${DASHBOARD_ID} .sfw-visual-grid, #${DASHBOARD_ID} .sfw-grid { display: grid; gap: 12px; grid-template-columns: repeat(2, minmax(0, 1fr)); }
			#${DASHBOARD_ID} .sfw-visual-grid { margin-bottom: 12px; }
			#${DASHBOARD_ID} .sfw-panel { background: #fff; border: 1px solid var(--sf-line); border-radius: 8px; box-shadow: 0 8px 22px rgba(0,72,138,.07); padding: 16px; }
			#${DASHBOARD_ID} .sfw-panel-title { color: var(--sf-blue-dark); font-size: 15px; font-weight: 800; margin-bottom: 10px; }
			#${DASHBOARD_ID} .sfw-health-visual, #${DASHBOARD_ID} .sfw-compliance-tracker-visual { align-items: center; display: grid; gap: 18px; grid-template-columns: auto minmax(0,1fr); min-height: 220px; }
			#${DASHBOARD_ID} .sfw-donut { align-items: center; background: conic-gradient(#eaecf0 0deg 360deg); border-radius: 50%; display: flex; height: 172px; justify-content: center; position: relative; width: 172px; }
			#${DASHBOARD_ID} .sfw-donut::after { background: #fff; border-radius: 50%; content: ""; height: 112px; position: absolute; width: 112px; }
			#${DASHBOARD_ID} .sfw-donut-center { color: var(--sf-ink); display: grid; font-size: 12px; font-weight: 700; justify-items: center; position: relative; z-index: 1; }
			#${DASHBOARD_ID} .sfw-donut-center strong { color: var(--sf-blue-dark); font-size: 28px; line-height: 1; }
			#${DASHBOARD_ID} .sfw-legend { display: grid; gap: 10px; }
			#${DASHBOARD_ID} .sfw-legend-row { align-items: center; background: transparent; border: 0; color: inherit; cursor: pointer; display: grid; gap: 8px; grid-template-columns: auto minmax(0,1fr) auto; padding: 0; text-align: left; width: 100%; }
			#${DASHBOARD_ID} .sfw-dot { border-radius: 50%; height: 10px; width: 10px; }
			#${DASHBOARD_ID} .sfw-dot.green, #${DASHBOARD_ID} .sfw-funnel-bar.green, #${DASHBOARD_ID} .sfw-expiry-fill.green { background: #08763d; }
			#${DASHBOARD_ID} .sfw-dot.orange, #${DASHBOARD_ID} .sfw-funnel-bar.orange, #${DASHBOARD_ID} .sfw-expiry-fill.orange { background: #b76b00; }
			#${DASHBOARD_ID} .sfw-dot.red, #${DASHBOARD_ID} .sfw-funnel-bar.red, #${DASHBOARD_ID} .sfw-expiry-fill.red { background: #b42318; }
			#${DASHBOARD_ID} .sfw-dot.blue, #${DASHBOARD_ID} .sfw-funnel-bar.blue, #${DASHBOARD_ID} .sfw-expiry-fill.blue { background: #005aa8; }
			#${DASHBOARD_ID} .sfw-dot.gray, #${DASHBOARD_ID} .sfw-funnel-bar.gray, #${DASHBOARD_ID} .sfw-expiry-fill.gray { background: #667085; }
			#${DASHBOARD_ID} .sfw-funnel-row { background: transparent; border: 0; cursor: pointer; display: grid; gap: 6px; padding: 0; text-align: left; width: 100%; margin-bottom: 9px; }
			#${DASHBOARD_ID} .sfw-funnel-label { align-items: center; display: flex; justify-content: space-between; }
			#${DASHBOARD_ID} .sfw-funnel-track, #${DASHBOARD_ID} .sfw-expiry-track { background: #eef4fb; border-radius: 999px; height: 12px; overflow: hidden; }
			#${DASHBOARD_ID} .sfw-funnel-bar, #${DASHBOARD_ID} .sfw-expiry-fill { border-radius: inherit; display: block; height: 100%; }
			#${DASHBOARD_ID} .sfw-expiry-timeline { display: grid; gap: 8px; }
			#${DASHBOARD_ID} .sfw-expiry-band { background: #f8fbff; border: 1px solid #edf4fb; border-radius: 8px; padding: 10px 12px; }
			#${DASHBOARD_ID} .sfw-expiry-band-head { align-items: center; display: flex; justify-content: space-between; margin-bottom: 8px; }
			#${DASHBOARD_ID} .sfw-row, #${DASHBOARD_ID} .sfw-heatmap-row { align-items: center; background: #f8fbff; border: 1px solid #edf4fb; border-radius: 8px; cursor: pointer; display: grid; gap: 10px; grid-template-columns: minmax(0,1fr) auto; padding: 10px 12px; text-align: left; width: 100%; }
			#${DASHBOARD_ID} .sfw-heatmap-row { grid-template-columns: minmax(0,1.2fr) minmax(0,.9fr) auto; }
			#${DASHBOARD_ID} .sfw-row:hover, #${DASHBOARD_ID} .sfw-heatmap-row:hover { background: #fff; border-color: rgba(0,90,168,.28); }
			#${DASHBOARD_ID} .sfw-row strong, #${DASHBOARD_ID} .sfw-row span, #${DASHBOARD_ID} .sfw-heatmap-main, #${DASHBOARD_ID} .sfw-heatmap-meta { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
			#${DASHBOARD_ID} .sfw-row-meta { display: grid; gap: 3px; justify-items: end; }
			#${DASHBOARD_ID} .sfw-pill, #${DASHBOARD_ID} .sfw-heatmap-score { border-radius: 999px; font-size: 12px; font-weight: 800; padding: 4px 8px; }
			#${DASHBOARD_ID} .sfw-pill.green, #${DASHBOARD_ID} .sfw-heatmap-score.green { background: #e7f7ee; color: #08763d; }
			#${DASHBOARD_ID} .sfw-pill.orange, #${DASHBOARD_ID} .sfw-heatmap-score.orange { background: #fff4df; color: #9a5b00; }
			#${DASHBOARD_ID} .sfw-pill.red, #${DASHBOARD_ID} .sfw-heatmap-score.red { background: #ffe9e9; color: #b42318; }
			#${DASHBOARD_ID} .sfw-pill.blue { background: #eaf4ff; color: #005aa8; }
			#${DASHBOARD_ID} .sfw-pill.gray { background: #eef1f4; color: #4b5563; }
			#${DASHBOARD_ID} .sfw-predictor-row { align-items: center; border-bottom: 1px solid var(--sf-line); display: grid; gap: 8px; grid-template-columns: 1fr auto; min-height: 38px; }
			#${DASHBOARD_ID} .sfw-empty { background: var(--sf-blue-soft); border-radius: 8px; color: var(--sf-ink); padding: 12px; }
			#${DASHBOARD_ID} .text-green { color: #08763d; } #${DASHBOARD_ID} .text-orange { color: #b76b00; } #${DASHBOARD_ID} .text-red { color: #b42318; } #${DASHBOARD_ID} .text-blue { color: #005aa8; } #${DASHBOARD_ID} .text-gray { color: #4b5563; }
			@media (max-width: 991px) { #${DASHBOARD_ID} .sfw-visual-grid, #${DASHBOARD_ID} .sfw-grid { grid-template-columns: 1fr; } }
			@media (max-width: 575px) { #${DASHBOARD_ID} .sfw-hero, #${DASHBOARD_ID} .sfw-health-visual, #${DASHBOARD_ID} .sfw-row, #${DASHBOARD_ID} .sfw-heatmap-row { align-items: flex-start; grid-template-columns: 1fr; } #${DASHBOARD_ID} .sfw-hero { flex-direction: column; } }
		`;
		document.head.appendChild(style);
	}
})();
