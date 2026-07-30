frappe.ui.form.on("Contract Compliance Tracker", {
	setup(frm) {
		install_compliance_status_formatters(frm);
	},

	refresh(frm) {
		install_compliance_status_formatters(frm);
		render_compliance_dashboard(frm);
		render_header_compliance_indicator(frm);
		refresh_compliance_status_indicators(frm);

		if (frm.doc.contract) {
			frm.add_custom_button(__("Open Contract"), () => {
				frappe.set_route("Form", "Contract", frm.doc.contract);
			});
		}
	},

	validate(frm) {
		validate_empty_obligation_rows(frm);
	},

	contract(frm) {
		sync_contract_fields(frm);
	},

	onload_post_render(frm) {
		render_compliance_dashboard(frm);
		render_header_compliance_indicator(frm);
		refresh_compliance_status_indicators(frm);
	},

	table_ewpx_add: update_compliance_visuals,
	table_ewpx_remove: update_compliance_visuals,
	table_jpcz_add: update_compliance_visuals,
	table_jpcz_remove: update_compliance_visuals,
	table_dhlt_add: update_compliance_visuals,
	table_dhlt_remove: update_compliance_visuals,
	table_mmyd_add: update_compliance_visuals,
	table_mmyd_remove: update_compliance_visuals,
});

function sync_contract_fields(frm) {
	if (!frm.doc.contract) {
		frm.set_value({
			contract_type: "",
			contractor: "",
		});
		return;
	}

	frappe.db
		.get_value("Contract", frm.doc.contract, ["sf_contract_type", "sf_contractor"])
		.then(({ message }) => {
			if (!message) {
				return;
			}

			frm.set_value({
				contract_type: message.sf_contract_type || "",
				contractor: message.sf_contractor || "",
			});
		});
}

frappe.ui.form.on("Contract Table 1", {
	compliance_status(frm) {
		render_compliance_dashboard(frm);
		refresh_compliance_status_indicators(frm);
	},

	form_render(frm) {
		render_compliance_dashboard(frm);
		refresh_compliance_status_indicators(frm);
	},
});

const compliance_table_fields = [
	{
		fieldname: "table_ewpx",
		term: "term",
		risk: "risk",
		label: "Term 1",
		obligation_label: "Obligation Table 1",
	},
	{
		fieldname: "table_jpcz",
		term: "term_2",
		risk: "risk_2",
		label: "Term 2",
		obligation_label: "Obligation Table 2",
	},
	{
		fieldname: "table_dhlt",
		term: "term_3",
		risk: "risk_3",
		label: "Term 3",
		obligation_label: "Obligation Table 3",
	},
	{
		fieldname: "table_mmyd",
		term: "term_4",
		risk: "risk_4",
		label: "Term 4",
		obligation_label: "Obligation 4",
	},
];

function update_compliance_visuals(frm) {
	render_compliance_dashboard(frm);
	render_header_compliance_indicator(frm);
	refresh_compliance_status_indicators(frm);
}

function validate_empty_obligation_rows(frm) {
	for (const table of compliance_table_fields) {
		const empty_row = (frm.doc[table.fieldname] || []).find(is_empty_obligation_row);

		if (empty_row) {
			frappe.validated = false;
			frappe.throw({
				title: __("Empty Obligation Row"),
				message: __("{0}, row {1} is empty. Please fill in the row or delete it before saving.", [
					table.obligation_label,
					empty_row.idx,
				]),
			});
		}
	}
}

function is_empty_obligation_row(row) {
	const obligation_fields = [
		"contractual_obligation",
		"responsible_person",
		"evidence_required",
		"compliance_status",
		"remarks__action",
	];

	return !obligation_fields.some((fieldname) => String(row[fieldname] || "").trim());
}

function install_compliance_status_formatters(frm) {
	inject_compliance_status_styles();

	compliance_table_fields.forEach(({ fieldname: table_fieldname }) => {
		const grid = frm.fields_dict[table_fieldname]?.grid;
		const compliance_field = grid?.get_field("compliance_status");

		if (!compliance_field || compliance_field.sf_status_formatter_installed) {
			return;
		}

		compliance_field.sf_status_formatter_installed = true;
		compliance_field.formatter = (value) => get_compliance_status_badge(value);
	});
}

function refresh_compliance_status_indicators(frm) {
	setTimeout(() => {
		compliance_table_fields.forEach(({ fieldname: table_fieldname }) => {
			const grid = frm.fields_dict[table_fieldname]?.grid;

			if (!grid) {
				return;
			}

			grid.refresh();
			paint_compliance_status_grid_cells(grid);
		});
	}, 100);
}

function render_compliance_dashboard(frm) {
	inject_compliance_status_styles();

	const dashboard = frm.fields_dict.sf_compliance_dashboard;

	if (!dashboard) {
		return;
	}

	const summary = get_compliance_summary(frm);
	dashboard.$wrapper.html(get_compliance_dashboard_html(summary));
}

function render_header_compliance_indicator(frm) {
	const summary = get_compliance_summary(frm);

	if (!summary.total) {
		frm.page.set_indicator(__("No Obligations"), "gray");
		return;
	}

	let color = "green";

	if (summary.non_compliant) {
		color = "red";
	} else if (summary.pending) {
		color = "orange";
	}

	frm.page.set_indicator(__("{0}% Compliant", [summary.percentage]), color);
}

function get_compliance_summary(frm) {
	const summary = {
		total: 0,
		compliant: 0,
		non_compliant: 0,
		pending: 0,
		term_rows: [],
	};

	compliance_table_fields.forEach((table) => {
		const rows = frm.doc[table.fieldname] || [];
		const term_label = frm.doc[table.term] || table.label;
		const term_summary = {
			label: term_label,
			risk: frm.doc[table.risk] || "",
			total: rows.length,
			compliant: 0,
			non_compliant: 0,
			pending: 0,
		};

		rows.forEach((row) => {
			const status_class = get_compliance_status_class(row.compliance_status);

			summary.total += 1;

			if (status_class === "compliant") {
				summary.compliant += 1;
				term_summary.compliant += 1;
			} else if (status_class === "non-compliant") {
				summary.non_compliant += 1;
				term_summary.non_compliant += 1;
			} else {
				summary.pending += 1;
				term_summary.pending += 1;
			}
		});

		if (term_summary.total) {
			summary.term_rows.push(term_summary);
		}
	});

	summary.percentage = summary.total ? Math.round((summary.compliant / summary.total) * 100) : 0;
	return summary;
}

function get_compliance_dashboard_html(summary) {
	const status_label = summary.total ? `${summary.percentage}% Compliant` : "No Items";
	const progress_class = summary.non_compliant ? "risk" : "clear";

	return `
		<div class="sf-compliance-dashboard">
			<div class="sf-compliance-dashboard-header">
				<div>
					<div class="sf-compliance-dashboard-title">${__("Compliance Overview")}</div>
					<div class="sf-compliance-dashboard-subtitle">${__("Calculated from the obligation tables below.")}</div>
				</div>
				<div class="sf-compliance-score ${progress_class}">
					<span>${frappe.utils.escape_html(status_label)}</span>
				</div>
			</div>

			<div class="sf-compliance-progress">
				<div class="sf-compliance-progress-bar ${progress_class}" style="width: ${summary.percentage}%"></div>
			</div>

			<div class="sf-compliance-cards">
				${get_summary_card_html(__("Total Obligations"), summary.total, "total")}
				${get_summary_card_html(__("Compliant"), summary.compliant, "compliant")}
				${get_summary_card_html(__("Non-Compliant"), summary.non_compliant, "non-compliant")}
				${get_summary_card_html(__("Pending"), summary.pending, "pending")}
			</div>
		</div>
	`;
}

function get_summary_card_html(label, value, status_class) {
	return `
		<div class="sf-compliance-summary-card ${status_class}">
			<div class="sf-compliance-summary-label">${frappe.utils.escape_html(label)}</div>
			<div class="sf-compliance-summary-value">${frappe.utils.escape_html(String(value))}</div>
		</div>
	`;
}

function paint_compliance_status_grid_cells(grid) {
	grid.grid_rows?.forEach((grid_row) => {
		const value = grid_row.doc?.compliance_status;
		const status_class = get_compliance_status_class(value);
		const $cell = grid_row.row?.find('[data-fieldname="compliance_status"]');
		const $static_area = $cell?.find(".static-area");

		if (!$cell?.length) {
			return;
		}

		$cell
			.removeClass("sf-compliance-cell-compliant sf-compliance-cell-non-compliant")
			.addClass(status_class ? `sf-compliance-cell-${status_class}` : "");

		if ($static_area?.length && !$cell.hasClass("editable")) {
			$static_area.html(get_compliance_status_badge(value));
		}
	});
}

function get_compliance_status_badge(value) {
	const status_class = get_compliance_status_class(value);
	const display_value = value || __("Pending");

	if (!status_class) {
		return `<span class="sf-compliance-status-badge sf-compliance-status-pending">
			${frappe.utils.escape_html(display_value)}
		</span>`;
	}

	return `<span class="sf-compliance-status-badge sf-compliance-status-${status_class}">
		${frappe.utils.escape_html(__(display_value))}
	</span>`;
}

function get_compliance_status_class(value) {
	const normalized = (value || "").toLowerCase().replace(/\s+/g, " ").trim();

	if (normalized === "compliant") {
		return "compliant";
	}

	if (normalized === "non- compliant" || normalized === "non-compliant") {
		return "non-compliant";
	}

	return "";
}

function inject_compliance_status_styles() {
	if (document.getElementById("sf-compliance-status-styles")) {
		return;
	}

	const style = document.createElement("style");
	style.id = "sf-compliance-status-styles";
	style.textContent = `
		.sf-compliance-status-badge {
			display: inline-flex;
			align-items: center;
			min-height: 24px;
			padding: 3px 10px;
			border-radius: 999px;
			font-size: 12px;
			font-weight: 700;
			letter-spacing: 0;
			line-height: 1.2;
			border: 1px solid transparent;
		}

		.sf-compliance-status-compliant {
			color: #067647;
			background: #dcfae6;
			border-color: #abefc6;
		}

		.sf-compliance-status-non-compliant {
			color: #b42318;
			background: #fee4e2;
			border-color: #fecdca;
		}

		.sf-compliance-status-pending {
			color: #b54708;
			background: #fef0c7;
			border-color: #fedf89;
		}

		.sf-compliance-cell-compliant,
		.sf-compliance-cell-non-compliant {
			border-radius: 6px;
		}

		.sf-compliance-dashboard {
			margin: 10px 0 18px;
			padding: 16px;
			border: 1px solid #d6e4f7;
			border-radius: 8px;
			background: linear-gradient(180deg, #f8fbff 0%, #ffffff 100%);
			box-shadow: 0 8px 20px rgba(16, 24, 40, 0.06);
		}

		.sf-compliance-dashboard-header {
			display: flex;
			align-items: flex-start;
			justify-content: space-between;
			gap: 16px;
			margin-bottom: 12px;
		}

		.sf-compliance-dashboard-title {
			color: #064f9e;
			font-size: 16px;
			font-weight: 800;
			line-height: 1.3;
		}

		.sf-compliance-dashboard-subtitle,
		.sf-compliance-term-meta,
		.sf-compliance-summary-label,
		.sf-compliance-empty {
			color: #667085;
			font-size: 12px;
		}

		.sf-compliance-score {
			min-width: 120px;
			padding: 8px 12px;
			border-radius: 8px;
			text-align: center;
			font-size: 18px;
			font-weight: 800;
			border: 1px solid;
		}

		.sf-compliance-score.clear {
			color: #067647;
			background: #ecfdf3;
			border-color: #abefc6;
		}

		.sf-compliance-score.risk {
			color: #b42318;
			background: #fef3f2;
			border-color: #fecdca;
		}

		.sf-compliance-progress {
			height: 8px;
			overflow: hidden;
			border-radius: 999px;
			background: #e4e7ec;
			margin-bottom: 14px;
		}

		.sf-compliance-progress-bar {
			height: 100%;
			border-radius: inherit;
			transition: width 0.25s ease;
		}

		.sf-compliance-progress-bar.clear {
			background: #12b76a;
		}

		.sf-compliance-progress-bar.risk {
			background: #f04438;
		}

		.sf-compliance-cards {
			display: grid;
			grid-template-columns: repeat(4, minmax(0, 1fr));
			gap: 10px;
			margin-bottom: 14px;
		}

		.sf-compliance-summary-card {
			padding: 10px 12px;
			border-radius: 8px;
			border: 1px solid #eaecf0;
			background: #ffffff;
		}

		.sf-compliance-summary-card.total {
			border-color: #b2ddff;
			background: #eff8ff;
		}

		.sf-compliance-summary-card.compliant {
			border-color: #abefc6;
			background: #ecfdf3;
		}

		.sf-compliance-summary-card.non-compliant {
			border-color: #fecdca;
			background: #fef3f2;
		}

		.sf-compliance-summary-card.pending {
			border-color: #fedf89;
			background: #fffaeb;
		}

		.sf-compliance-summary-value {
			color: #101828;
			font-size: 22px;
			font-weight: 800;
			line-height: 1.1;
			margin-top: 4px;
		}

		.sf-mini-pill {
			display: inline-flex;
			align-items: center;
			justify-content: center;
			min-width: 24px;
			height: 22px;
			padding: 0 7px;
			border-radius: 999px;
			font-size: 12px;
			font-weight: 700;
		}

		.sf-mini-pill.compliant {
			color: #067647;
			background: #dcfae6;
		}

		.sf-mini-pill.non-compliant {
			color: #b42318;
			background: #fee4e2;
		}

		.sf-mini-pill.pending {
			color: #b54708;
			background: #fef0c7;
		}

		@media (max-width: 768px) {
			.sf-compliance-dashboard-header {
				flex-direction: column;
				align-items: stretch;
			}

			.sf-compliance-score {
				width: 100%;
			}

			.sf-compliance-cards {
				grid-template-columns: repeat(2, minmax(0, 1fr));
			}
		}
	`;
	document.head.appendChild(style);
}
