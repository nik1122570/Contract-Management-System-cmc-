frappe.ui.form.on("Contract Compliance Tracker", {
	setup(frm) {
		install_compliance_status_formatters(frm);
	},

	refresh(frm) {
		install_compliance_status_formatters(frm);
		render_compliance_dashboard(frm);
		render_header_compliance_indicator(frm);
		refresh_compliance_status_indicators(frm);

		frm.add_custom_button(__("Preview Obligations"), () => {
			show_obligations_preview(frm);
		});

		if (!frm.is_new()) {
			frm.add_custom_button(__("Create Next Month Tracker"), () => {
				create_next_month_tracker(frm);
			});
		}

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
		obligation_label: "Compliance Obligations",
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
	];

	return !obligation_fields.some((fieldname) => String(row[fieldname] || "").trim());
}

function install_compliance_status_formatters(frm) {
	inject_compliance_status_styles();

	compliance_table_fields.forEach(({ fieldname: table_fieldname }) => {
		const grid = frm.fields_dict[table_fieldname]?.grid;
		const compliance_field = grid?.get_field("compliance_status");
		const terms_field = grid?.get_field("terms");

		if (compliance_field && !compliance_field.sf_status_formatter_installed) {
			compliance_field.sf_status_formatter_installed = true;
			compliance_field.formatter = (value) => get_compliance_status_badge(value);
		}

		if (terms_field && !terms_field.sf_status_dot_formatter_installed) {
			terms_field.sf_status_dot_formatter_installed = true;
			terms_field.formatter = (value, df, options, doc) => get_term_status_html(value, doc?.compliance_status);
		}
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
		rows.forEach((row) => {
			const status_class = get_compliance_status_class(row.compliance_status);

			summary.total += 1;

			if (status_class === "compliant") {
				summary.compliant += 1;
			} else if (status_class === "non-compliant") {
				summary.non_compliant += 1;
			} else {
				summary.pending += 1;
			}
		});
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
					<div class="sf-compliance-dashboard-subtitle">${__("Calculated from the compliance obligations table below.")}</div>
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

function create_next_month_tracker(frm) {
	if (frm.is_dirty()) {
		frappe.throw(__("Please save this tracker before creating the next month tracker."));
	}

	frappe.confirm(
		__(
			"Create a new tracker for the next month using the same Contract and obligation rows? Compliance Status will be left blank for fresh evaluation."
		),
		() => {
			frappe.call({
				method:
					"sf_contracts.sf_contracts.doctype.contract_compliance_tracker.contract_compliance_tracker.create_next_month_tracker",
				args: {
					source_name: frm.doc.name,
				},
				freeze: true,
				freeze_message: __("Creating next month tracker..."),
				callback(response) {
					if (!response.message?.name) {
						return;
					}

					frappe.show_alert(
						{
							message: __("Next month tracker {0} created.", [response.message.name]),
							indicator: "green",
						},
						6
					);
					frappe.set_route("Form", "Contract Compliance Tracker", response.message.name);
				},
			});
		}
	);
}

function show_obligations_preview(frm) {
	inject_compliance_status_styles();

	const rows = get_obligation_preview_rows(frm);
	const summary = get_compliance_summary(frm);

	const dialog = new frappe.ui.Dialog({
		title: __("Compliance Obligations Preview"),
		size: "extra-large",
		fields: [
			{
				fieldtype: "HTML",
				fieldname: "preview_html",
				options: get_obligations_preview_html(rows, summary),
			},
		],
	});

	dialog.show();
	install_obligation_preview_filters(dialog.$wrapper);
}

function get_obligation_preview_rows(frm) {
	return (frm.doc.table_ewpx || []).map((row) => {
		const status_class = get_compliance_status_class(row.compliance_status) || "pending";
		const status_label = row.compliance_status || __("Pending");
		const risk_label = row.risk || __("Not Set");

		return {
			idx: row.idx,
			terms: row.terms || __("No Term"),
			contractual_obligation: row.contractual_obligation || "",
			responsible_person: row.responsible_person || "",
			evidence_required: row.evidence_required || "",
			compliance_status: status_label,
			status_class,
			risk: risk_label,
			filter_keys: ["all", status_class, String(risk_label).toLowerCase() === "high" ? "high-risk" : ""]
				.filter(Boolean)
				.join(" "),
		};
	});
}

function get_obligations_preview_html(rows, summary) {
	const empty_state = `
		<div class="sf-obligation-preview-empty">
			${__("No compliance obligations have been added yet.")}
		</div>
	`;

	return `
		<div class="sf-obligation-preview">
			<div class="sf-obligation-preview-top">
				<div>
					<div class="sf-obligation-preview-title">${__("Compliance Obligations")}</div>
					<div class="sf-obligation-preview-subtitle">
						${__("Readable preview of the child table data for review and discussion.")}
					</div>
				</div>
				<div class="sf-obligation-preview-score ${summary.non_compliant ? "risk" : "clear"}">
					<span>${frappe.utils.escape_html(String(summary.percentage))}%</span>
					<small>${__("Compliant")}</small>
				</div>
			</div>

			<div class="sf-obligation-preview-stats">
				${get_preview_stat_html(__("Total Obligations"), summary.total, "total")}
				${get_preview_stat_html(__("Compliant"), summary.compliant, "compliant")}
				${get_preview_stat_html(__("Non-Compliant"), summary.non_compliant, "non-compliant")}
				${get_preview_stat_html(__("Pending"), summary.pending, "pending")}
			</div>

			<div class="sf-obligation-preview-filters" role="group" aria-label="${__("Filter obligations")}">
				${get_preview_filter_html("all", __("All"), true)}
				${get_preview_filter_html("compliant", __("Compliant"))}
				${get_preview_filter_html("non-compliant", __("Non-Compliant"))}
				${get_preview_filter_html("pending", __("Pending"))}
				${get_preview_filter_html("high-risk", __("High Risk"))}
			</div>

			<div class="sf-obligation-preview-list">
				${rows.length ? rows.map(get_obligation_preview_card_html).join("") : empty_state}
			</div>
		</div>
	`;
}

function get_preview_stat_html(label, value, status_class) {
	return `
		<div class="sf-obligation-preview-stat ${status_class}">
			<span>${frappe.utils.escape_html(label)}</span>
			<strong>${frappe.utils.escape_html(String(value))}</strong>
		</div>
	`;
}

function get_preview_filter_html(filter, label, active = false) {
	return `
		<button type="button" class="sf-obligation-preview-filter ${active ? "active" : ""}" data-filter="${filter}">
			${frappe.utils.escape_html(label)}
		</button>
	`;
}

function get_obligation_preview_card_html(row) {
	return `
		<div class="sf-obligation-preview-card" data-filter-keys="${frappe.utils.escape_html(row.filter_keys)}">
			<div class="sf-obligation-preview-card-head">
				<div class="sf-obligation-preview-term">
					${get_term_status_html(row.terms, row.compliance_status)}
				</div>
				<div class="sf-obligation-preview-badges">
					${get_compliance_status_badge(row.compliance_status)}
					<span class="sf-obligation-preview-risk ${get_preview_risk_class(row.risk)}">
						${frappe.utils.escape_html(row.risk)}
					</span>
				</div>
			</div>
			<div class="sf-obligation-preview-body">
				<div class="sf-obligation-preview-field wide">
					<span>${__("Contractual Obligation")}</span>
					<p>${frappe.utils.escape_html(row.contractual_obligation || "-")}</p>
				</div>
				<div class="sf-obligation-preview-field">
					<span>${__("Responsible Person")}</span>
					<p>${frappe.utils.escape_html(row.responsible_person || "-")}</p>
				</div>
				<div class="sf-obligation-preview-field">
					<span>${__("Evidence Required")}</span>
					<p>${frappe.utils.escape_html(row.evidence_required || "-")}</p>
				</div>
			</div>
		</div>
	`;
}

function get_preview_risk_class(value) {
	const normalized = String(value || "").toLowerCase().trim();

	if (["high", "medium", "low"].includes(normalized)) {
		return normalized;
	}

	return "unset";
}

function install_obligation_preview_filters($wrapper) {
	$wrapper.find(".sf-obligation-preview-filter").on("click", function () {
		const $button = $(this);
		const filter = $button.data("filter");
		const $preview = $button.closest(".sf-obligation-preview");

		$preview.find(".sf-obligation-preview-filter").removeClass("active");
		$button.addClass("active");

		$preview.find(".sf-obligation-preview-card").each(function () {
			const keys = String($(this).data("filter-keys") || "").split(" ");
			$(this).toggle(keys.includes(filter));
		});

		const visible_count = $preview.find(".sf-obligation-preview-card:visible").length;
		$preview.find(".sf-obligation-preview-no-results").remove();

		if (!visible_count && $preview.find(".sf-obligation-preview-card").length) {
			$preview.find(".sf-obligation-preview-list").append(`
				<div class="sf-obligation-preview-no-results">
					${__("No obligations match this filter.")}
				</div>
			`);
		}
	});
}

function paint_compliance_status_grid_cells(grid) {
	grid.grid_rows?.forEach((grid_row) => {
		const value = grid_row.doc?.compliance_status;
		const status_class = get_compliance_status_class(value);
		const $cell = grid_row.row?.find('[data-fieldname="compliance_status"]');
		const $static_area = $cell?.find(".static-area");
		const $terms_cell = grid_row.row?.find('[data-fieldname="terms"]');
		const $terms_static_area = $terms_cell?.find(".static-area");

		if ($cell?.length) {
			$cell
				.removeClass("sf-compliance-cell-compliant sf-compliance-cell-non-compliant")
				.addClass(status_class ? `sf-compliance-cell-${status_class}` : "");

			if ($static_area?.length && !$cell.hasClass("editable")) {
				$static_area.html(get_compliance_status_badge(value));
			}
		}

		if ($terms_cell?.length) {
			$terms_cell
				.removeClass("sf-term-cell-compliant sf-term-cell-non-compliant sf-term-cell-pending")
				.addClass(`sf-term-cell-${status_class || "pending"}`);

			if ($terms_static_area?.length && !$terms_cell.hasClass("editable")) {
				$terms_static_area.html(get_term_status_html(grid_row.doc?.terms, value));
			}
		}
	});
}

function get_term_status_html(value, compliance_status) {
	const status_class = get_compliance_status_class(compliance_status) || "pending";
	const display_value = value || "";

	return `<span class="sf-term-status ${status_class}">
		<span class="sf-term-status-dot"></span>
		<span class="sf-term-status-label">${frappe.utils.escape_html(display_value)}</span>
	</span>`;
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

		.sf-term-status {
			display: inline-flex;
			align-items: center;
			gap: 7px;
			max-width: 100%;
			font-weight: 700;
			line-height: 1.25;
			vertical-align: middle;
		}

		.sf-term-status-dot {
			display: inline-block;
			flex: 0 0 auto;
			width: 9px;
			height: 9px;
			border-radius: 999px;
			box-shadow: 0 0 0 3px rgba(102, 112, 133, 0.12);
		}

		.sf-term-status-label {
			min-width: 0;
			overflow: hidden;
			text-overflow: ellipsis;
			white-space: nowrap;
		}

		.sf-term-status.compliant .sf-term-status-dot {
			background: #12b76a;
			box-shadow: 0 0 0 3px rgba(18, 183, 106, 0.14);
		}

		.sf-term-status.non-compliant .sf-term-status-dot {
			background: #f04438;
			box-shadow: 0 0 0 3px rgba(240, 68, 56, 0.14);
		}

		.sf-term-status.pending .sf-term-status-dot {
			background: #f79009;
			box-shadow: 0 0 0 3px rgba(247, 144, 9, 0.14);
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

		.sf-obligation-preview {
			padding: 4px 0 2px;
		}

		.sf-obligation-preview,
		.sf-obligation-preview * {
			box-sizing: border-box;
		}

		.sf-obligation-preview-top {
			display: flex;
			align-items: flex-start;
			justify-content: space-between;
			gap: 16px;
			padding: 14px 16px;
			border-radius: 8px;
			background: #064f9e;
			color: #ffffff;
			margin-bottom: 12px;
		}

		.sf-obligation-preview-title {
			font-size: 18px;
			font-weight: 800;
			line-height: 1.25;
		}

		.sf-obligation-preview-subtitle {
			color: rgba(255, 255, 255, 0.82);
			font-size: 12px;
			margin-top: 3px;
		}

		.sf-obligation-preview-score {
			min-width: 112px;
			padding: 8px 12px;
			border-radius: 8px;
			text-align: center;
			background: #ffffff;
			border: 1px solid rgba(255, 255, 255, 0.55);
		}

		.sf-obligation-preview-score span {
			display: block;
			font-size: 24px;
			font-weight: 800;
			line-height: 1;
		}

		.sf-obligation-preview-score small {
			display: block;
			margin-top: 3px;
			font-size: 11px;
			font-weight: 700;
		}

		.sf-obligation-preview-score.clear {
			color: #067647;
		}

		.sf-obligation-preview-score.risk {
			color: #b42318;
		}

		.sf-obligation-preview-stats {
			display: grid;
			grid-template-columns: repeat(4, minmax(0, 1fr));
			gap: 10px;
			margin-bottom: 12px;
		}

		.sf-obligation-preview-stat {
			padding: 10px 12px;
			border-radius: 8px;
			border: 1px solid #d6e4f7;
			background: #f8fbff;
		}

		.sf-obligation-preview-stat span {
			display: block;
			color: #475467;
			font-size: 12px;
			line-height: 1.2;
		}

		.sf-obligation-preview-stat strong {
			display: block;
			color: #101828;
			font-size: 22px;
			line-height: 1.1;
			margin-top: 4px;
		}

		.sf-obligation-preview-stat.compliant {
			background: #ecfdf3;
			border-color: #abefc6;
		}

		.sf-obligation-preview-stat.non-compliant {
			background: #fef3f2;
			border-color: #fecdca;
		}

		.sf-obligation-preview-stat.pending {
			background: #fffaeb;
			border-color: #fedf89;
		}

		.sf-obligation-preview-filters {
			display: flex;
			flex-wrap: wrap;
			gap: 8px;
			margin-bottom: 12px;
		}

		.sf-obligation-preview-filter {
			border: 1px solid #d0d5dd;
			background: #ffffff;
			color: #344054;
			border-radius: 999px;
			padding: 6px 12px;
			font-size: 12px;
			font-weight: 700;
			line-height: 1.2;
		}

		.sf-obligation-preview-filter.active,
		.sf-obligation-preview-filter:hover {
			border-color: #064f9e;
			background: #eff8ff;
			color: #064f9e;
		}

		.sf-obligation-preview-list {
			display: flex;
			flex-direction: column;
			gap: 10px;
			max-height: none;
			overflow: visible;
			padding-right: 4px;
		}

		.sf-obligation-preview-card {
			border: 1px solid #d6e4f7;
			border-radius: 8px;
			background: #ffffff;
			overflow: visible;
		}

		.sf-obligation-preview-card-head {
			display: flex;
			align-items: center;
			justify-content: space-between;
			gap: 12px;
			padding: 10px 12px;
			background: #f8fbff;
			border-bottom: 1px solid #eaecf0;
		}

		.sf-obligation-preview-term {
			min-width: 0;
			font-size: 14px;
		}

		.sf-obligation-preview-badges {
			display: flex;
			align-items: center;
			flex-wrap: wrap;
			justify-content: flex-end;
			gap: 8px;
		}

		.sf-obligation-preview-risk {
			display: inline-flex;
			align-items: center;
			min-height: 24px;
			padding: 3px 10px;
			border-radius: 999px;
			font-size: 12px;
			font-weight: 700;
			border: 1px solid #d0d5dd;
			color: #475467;
			background: #f9fafb;
		}

		.sf-obligation-preview-risk.high {
			color: #b42318;
			background: #fef3f2;
			border-color: #fecdca;
		}

		.sf-obligation-preview-risk.medium {
			color: #b54708;
			background: #fffaeb;
			border-color: #fedf89;
		}

		.sf-obligation-preview-risk.low {
			color: #067647;
			background: #ecfdf3;
			border-color: #abefc6;
		}

		.sf-obligation-preview-body {
			display: grid;
			grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
			align-items: start;
			gap: 14px;
			padding: 12px;
		}

		.sf-obligation-preview-field.wide {
			grid-column: 1 / -1;
		}

		.sf-obligation-preview-field span {
			display: block;
			color: #667085;
			font-size: 11px;
			font-weight: 700;
			text-transform: uppercase;
			letter-spacing: 0;
			margin-bottom: 4px;
		}

		.sf-obligation-preview-field p {
			color: #101828;
			font-size: 13px;
			line-height: 1.45;
			margin: 0;
			white-space: pre-wrap;
			overflow: visible;
			overflow-wrap: anywhere;
			word-break: normal;
		}

		.sf-obligation-preview-empty,
		.sf-obligation-preview-no-results {
			padding: 16px;
			border-radius: 8px;
			background: #eff8ff;
			color: #064f9e;
			font-weight: 600;
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

			.sf-obligation-preview-top,
			.sf-obligation-preview-card-head {
				flex-direction: column;
				align-items: stretch;
			}

			.sf-obligation-preview-score {
				width: 100%;
			}

			.sf-obligation-preview-stats,
			.sf-obligation-preview-body {
				grid-template-columns: 1fr;
			}
		}
	`;
	document.head.appendChild(style);
}
