(function () {
	const DASHBOARD_ID = "sf-kpi-workspace-dashboard";
	let render_timer = null;
	let observer_started = false;

	frappe.router.on("change", () => schedule_render());
	$(document).on("workspace_refresh", () => schedule_render());
	$(document).ready(() => {
		start_observer();
		schedule_render();
	});

	function schedule_render(attempt = 0) {
		clearTimeout(render_timer);
		render_timer = setTimeout(() => {
			const rendered = render_dashboard();
			if (!rendered && is_kpi_workspace() && attempt < 12) {
				schedule_render(attempt + 1);
			}
		}, attempt ? 350 : 100);
	}

	function start_observer() {
		if (observer_started || !document.body) {
			return;
		}
		observer_started = true;
		new MutationObserver(() => {
			if (is_kpi_workspace() && !$(`#${DASHBOARD_ID}`).length) {
				schedule_render();
			}
		}).observe(document.body, { childList: true, subtree: true });
	}

	function is_kpi_workspace() {
		const route = (frappe.get_route() || []).map((part) => String(part).toLowerCase());
		const title = $(".page-title .title-text, .page-title").first().text().trim().toLowerCase();
		return route.includes("kpi-management") || route.includes("kpi management") || title === "kpi management";
	}

	function render_dashboard() {
		if (!is_kpi_workspace()) {
			$(`#${DASHBOARD_ID}`).remove();
			return true;
		}

		if ($(`#${DASHBOARD_ID}`).length) {
			return true;
		}

		const $target = get_workspace_target();
		if (!$target.length) {
			return false;
		}

		$target.prepend(get_shell_html());
		frappe.call({
			method: "sf_contracts.kpi_management.get_kpi_workspace_dashboard",
			callback(response) {
				render_content(response.message || {});
			},
		});
		return true;
	}

	function get_workspace_target() {
		for (const selector of [
			".layout-main-section .workspace-body",
			".layout-main-section .workspace-content",
			".layout-main-section",
		]) {
			const $target = $(selector).first();
			if ($target.length) {
				return $target;
			}
		}
		return $();
	}

	function get_shell_html() {
		return `
			<div id="${DASHBOARD_ID}" class="sfkpi-dashboard">
				<style>
					.sfkpi-dashboard {
						border: 1px solid #d7e7f7;
						border-radius: 8px;
						background: #fff;
						margin-bottom: 14px;
						overflow: hidden;
					}
					.sfkpi-hero {
						background: #005aa8;
						color: #fff;
						display: flex;
						align-items: center;
						justify-content: space-between;
						gap: 18px;
						padding: 18px 20px;
					}
					.sfkpi-eyebrow {
						font-size: 11px;
						font-weight: 800;
						text-transform: uppercase;
						opacity: .9;
					}
					.sfkpi-title {
						font-size: 22px;
						font-weight: 800;
						line-height: 1.2;
						margin-top: 4px;
					}
					.sfkpi-subtitle {
						font-size: 12px;
						opacity: .92;
						margin-top: 5px;
					}
					.sfkpi-countdown {
						background: #fff;
						border-radius: 8px;
						color: #005aa8;
						min-width: 170px;
						padding: 10px 14px;
						text-align: center;
					}
					.sfkpi-days {
						font-size: 30px;
						font-weight: 900;
						line-height: 1;
					}
					.sfkpi-days-label {
						color: #3d5f80;
						font-size: 11px;
						font-weight: 800;
						margin-top: 3px;
						text-transform: uppercase;
					}
					.sfkpi-body {
						display: grid;
						grid-template-columns: 1.2fr 1fr;
						gap: 14px;
						padding: 14px;
					}
					.sfkpi-panel {
						border: 1px solid #d7e7f7;
						border-radius: 8px;
						padding: 13px;
					}
					.sfkpi-panel-title {
						color: #003f7d;
						font-size: 14px;
						font-weight: 800;
						margin-bottom: 10px;
					}
					.sfkpi-next-line {
						align-items: center;
						display: flex;
						justify-content: space-between;
						gap: 12px;
						border-bottom: 1px solid #e8f1fb;
						padding: 8px 0;
					}
					.sfkpi-next-line:last-child {
						border-bottom: 0;
					}
					.sfkpi-label {
						color: #667085;
						font-size: 11px;
						font-weight: 800;
						text-transform: uppercase;
					}
					.sfkpi-value {
						color: #101828;
						font-size: 14px;
						font-weight: 800;
						text-align: right;
					}
					.sfkpi-grid {
						display: grid;
						grid-template-columns: repeat(3, minmax(0, 1fr));
						gap: 10px;
					}
					.sfkpi-card {
						background: #f4f9ff;
						border: 1px solid #d7e7f7;
						border-radius: 8px;
						cursor: pointer;
						padding: 10px;
					}
					.sfkpi-card strong {
						color: #005aa8;
						display: block;
						font-size: 20px;
						line-height: 1.15;
					}
					.sfkpi-card span {
						color: #5b6b80;
						display: block;
						font-size: 11px;
						font-weight: 800;
						margin-top: 5px;
						text-transform: uppercase;
					}
					.sfkpi-card.orange strong { color: #b76b00; }
					.sfkpi-card.red strong { color: #b42318; }
					.sfkpi-card.green strong { color: #08763d; }
					.sfkpi-upcoming {
						margin-top: 12px;
					}
					.sfkpi-upcoming-row {
						background: #f8fbff;
						border: 1px solid #e2edf8;
						border-radius: 8px;
						display: flex;
						justify-content: space-between;
						gap: 10px;
						margin-top: 8px;
						padding: 9px 10px;
					}
					.sfkpi-upcoming-row b {
						color: #101828;
					}
					.sfkpi-upcoming-row span {
						color: #667085;
						font-size: 12px;
					}
					@media (max-width: 900px) {
						.sfkpi-hero,
						.sfkpi-body {
							display: block;
						}
						.sfkpi-countdown,
						.sfkpi-panel {
							margin-top: 12px;
						}
						.sfkpi-grid {
							grid-template-columns: 1fr;
						}
					}
				</style>
				<div class="sfkpi-hero">
					<div>
						<div class="sfkpi-eyebrow">SF Group KPI Management</div>
						<div class="sfkpi-title">KPI Review Countdown</div>
						<div class="sfkpi-subtitle">Shows when the next KPI review will be generated and what is pending right now.</div>
					</div>
					<div class="sfkpi-countdown">
						<div class="sfkpi-days">...</div>
						<div class="sfkpi-days-label">Days to Next KPI</div>
					</div>
				</div>
				<div class="sfkpi-body">
					<div class="sfkpi-panel">
						<div class="sfkpi-panel-title">Next KPI Review</div>
						<div class="sfkpi-next-details"></div>
					</div>
					<div class="sfkpi-panel">
						<div class="sfkpi-panel-title">KPI Action Snapshot</div>
						<div class="sfkpi-grid"></div>
					</div>
				</div>
			</div>
		`;
	}

	function render_content(data) {
		const next = data.next_event || {};
		const counts = data.counts || {};
		const upcoming = data.upcoming || [];
		const days = next.days;

		$(`#${DASHBOARD_ID} .sfkpi-days`).text(days == null ? "-" : days < 0 ? "Due" : days);
		$(`#${DASHBOARD_ID} .sfkpi-days-label`).text(days == null ? __("No Active KPI") : days === 1 ? __("Day to Next KPI") : __("Days to Next KPI"));

		$(`#${DASHBOARD_ID} .sfkpi-next-details`).html(`
			${detail_line(__("Next Review Date"), next.date ? frappe.datetime.str_to_user(next.date) : __("No active assignment"))}
			${detail_line(__("Review Period"), (next.periods || []).join(", ") || "-")}
			${detail_line(__("Frequency"), (next.frequency || []).join(", ") || "-")}
			${detail_line(__("Assignments Due"), cint(next.assignments || 0))}
		`);

		$(`#${DASHBOARD_ID} .sfkpi-grid`).html(`
			${snapshot_card(__("Active Assignments"), counts.active_assignments, "KPI Structure Assignment", {}, "")}
			${snapshot_card(__("Pending Self Rating"), counts.pending_self_rating, "KPI Review", { workflow_status: "Pending Self Rating" }, "orange")}
			${snapshot_card(__("Pending Final Rating"), counts.pending_final_rating, "KPI Review", { workflow_status: "Pending Final Rating" }, "orange")}
			${snapshot_card(__("Overdue Self Rating"), counts.overdue_self_rating, "Overdue KPI Reviews", { overdue_stage: "Self Rating" }, "red", true)}
			${snapshot_card(__("Overdue Final Rating"), counts.overdue_final_rating, "Overdue KPI Reviews", { overdue_stage: "Final Rating" }, "red", true)}
			${snapshot_card(__("Completed Reviews"), counts.completed_reviews, "KPI Review", { workflow_status: "Completed" }, "green")}
		`);

		const upcoming_html = upcoming.length
			? upcoming.map((row) => `
				<div class="sfkpi-upcoming-row">
					<div><b>${escape_html(row.employee_name || row.employee || "-")}</b><br><span>${escape_html(row.period_key)} · ${escape_html(row.review_frequency)}</span></div>
					<div><b>${frappe.datetime.str_to_user(row.next_review_date)}</b><br><span>${cint(row.days_to_next_review)} ${__("days")}</span></div>
				</div>
			`).join("")
			: `<div class="text-muted">${__("No upcoming KPI review found.")}</div>`;

		$(`#${DASHBOARD_ID} .sfkpi-next-details`).append(`
			<div class="sfkpi-upcoming">
				<div class="sfkpi-label">${__("Upcoming Assignments")}</div>
				${upcoming_html}
			</div>
		`);

		$(`#${DASHBOARD_ID} .sfkpi-card`).on("click", function () {
			const doctype = $(this).attr("data-doctype");
			const is_report = cint($(this).attr("data-report"));
			const route_options = JSON.parse($(this).attr("data-route-options") || "{}");
			frappe.route_options = route_options;
			if (is_report) {
				frappe.set_route("query-report", doctype);
			} else {
				frappe.set_route("List", doctype);
			}
		});
	}

	function detail_line(label, value) {
		return `
			<div class="sfkpi-next-line">
				<div class="sfkpi-label">${escape_html(label)}</div>
				<div class="sfkpi-value">${escape_html(value)}</div>
			</div>
		`;
	}

	function snapshot_card(label, value, doctype, route_options, color, is_report = false) {
		return `
			<button class="sfkpi-card ${color || ""}" data-doctype="${escape_html(doctype)}" data-report="${is_report ? 1 : 0}" data-route-options='${escape_html(JSON.stringify(route_options || {}))}'>
				<strong>${cint(value || 0)}</strong>
				<span>${escape_html(label)}</span>
			</button>
		`;
	}

	function escape_html(value) {
		return frappe.utils.escape_html(String(value ?? ""));
	}
})();
