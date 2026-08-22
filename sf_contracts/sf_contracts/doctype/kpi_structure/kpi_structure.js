frappe.ui.form.on("KPI Structure", {
	refresh(frm) {
		update_total_weight(frm);
		frm.add_custom_button(__("Preview Components"), () => show_components_preview(frm));
		if (frm.doc.docstatus === 1 && frm.doc.status === "Active") {
			frm.add_custom_button(__("Assign in Bulk"), () => show_bulk_assignment_dialog(frm));
		}
	},
	components_add(frm) {
		update_total_weight(frm);
	},
	components_remove(frm) {
		update_total_weight(frm);
	},
});

frappe.ui.form.on("KPI Structure Item", {
	weight(frm) {
		update_total_weight(frm);
	},
	target_operator(frm, cdt, cdn) {
		update_target_display(frm, cdt, cdn);
	},
	target_value(frm, cdt, cdn) {
		update_target_display(frm, cdt, cdn);
	},
	target_value_2(frm, cdt, cdn) {
		update_target_display(frm, cdt, cdn);
	},
});

function update_total_weight(frm) {
	const total = (frm.doc.components || []).reduce((sum, row) => sum + flt(row.weight), 0);
	frm.set_value("total_weight", total);
}

function update_target_display(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	row.target_display =
		row.target_operator === "Range"
			? `${row.target_value || 0} - ${row.target_value_2 || 0}`
			: `${row.target_operator || ""} ${row.target_value || 0}`.trim();
	frm.refresh_field("components");
}

function show_bulk_assignment_dialog(frm) {
	const dialog = new frappe.ui.Dialog({
		title: __("Bulk KPI Structure Assignment"),
		size: "large",
		fields: [
			{
				fieldname: "employees",
				fieldtype: "Table",
				label: __("Employees"),
				cannot_add_rows: false,
				in_place_edit: true,
				reqd: 1,
				fields: [
					{
						fieldname: "employee",
						fieldtype: "Link",
						label: __("Employee"),
						options: "Employee",
						in_list_view: 1,
						reqd: 1,
						get_query: () => ({
							filters: {
								status: "Active",
								designation: frm.doc.designation,
								...(frm.doc.company ? { company: frm.doc.company } : {}),
							},
						}),
					},
					{
						fieldname: "employee_name",
						fieldtype: "Data",
						label: __("Employee Name"),
						in_list_view: 1,
						read_only: 1,
					},
				],
			},
			{
				fieldname: "dates_section",
				fieldtype: "Section Break",
				label: __("Assignment Details"),
			},
			{
				fieldname: "start_date",
				fieldtype: "Date",
				label: __("Start Date"),
				default: frm.doc.effective_from,
				reqd: 1,
			},
			{
				fieldname: "end_date",
				fieldtype: "Date",
				label: __("End Date"),
				default: frm.doc.effective_to,
				reqd: 1,
			},
			{
				fieldname: "column_break_1",
				fieldtype: "Column Break",
			},
			{
				fieldname: "review_frequency",
				fieldtype: "Select",
				label: __("Review Frequency"),
				options: "Monthly\nQuarterly\nSemi-Annual",
				default: "Quarterly",
				reqd: 1,
			},
			{
				fieldname: "submit_assignments",
				fieldtype: "Check",
				label: __("Submit Assignments"),
				default: 1,
			},
			{
				fieldname: "due_section",
				fieldtype: "Section Break",
				label: __("Due Days"),
			},
			{
				fieldname: "self_rating_due_days",
				fieldtype: "Int",
				label: __("Self-rating Due Days"),
				default: 7,
				reqd: 1,
			},
			{
				fieldname: "final_rating_due_days",
				fieldtype: "Int",
				label: __("Final-rating Due Days"),
				default: 7,
				reqd: 1,
			},
		],
		primary_action_label: __("Create Assignments"),
		primary_action(values) {
			const employees = (values.employees || []).filter((row) => row.employee);
			if (!employees.length) {
				frappe.throw(__("Please select at least one Employee."));
			}

			frappe.call({
				method:
					"sf_contracts.sf_contracts.doctype.kpi_structure.kpi_structure.bulk_assign_kpi_structure",
				args: {
					kpi_structure: frm.doc.name,
					employees,
					start_date: values.start_date,
					end_date: values.end_date,
					review_frequency: values.review_frequency,
					self_rating_due_days: values.self_rating_due_days,
					final_rating_due_days: values.final_rating_due_days,
					submit_assignments: values.submit_assignments ? 1 : 0,
				},
				freeze: true,
				freeze_message: __("Creating KPI Structure Assignments..."),
				callback(response) {
					dialog.hide();
					show_bulk_assignment_result(response.message || {});
				},
			});
		},
	});

	dialog.fields_dict.employees.grid.wrapper.on("change", 'input[data-fieldname="employee"]', () => {
		update_employee_names(dialog);
	});

	dialog.show();
}

function show_components_preview(frm) {
	const components = frm.doc.components || [];
	if (!components.length) {
		frappe.msgprint(__("No KPI components have been added."));
		return;
	}

	const dialog = new frappe.ui.Dialog({
		title: __("KPI Components Preview"),
		size: "extra-large",
		fields: [
			{
				fieldname: "preview",
				fieldtype: "HTML",
			},
		],
	});

	dialog.fields_dict.preview.$wrapper.html(get_components_preview_html(frm, components));
	dialog.show();
}

function get_components_preview_html(frm, components) {
	const total_weight = components.reduce((sum, row) => sum + flt(row.weight), 0);
	const grouped = components.reduce((groups, row) => {
		const key = row.perspective || __("No Perspective");
		groups[key] = groups[key] || [];
		groups[key].push(row);
		return groups;
	}, {});

	const css = `
		<style>
			.kpi-preview-wrap {
				max-height: 70vh;
				overflow: auto;
				padding: 4px 2px 12px;
			}
			.kpi-preview-summary {
				display: grid;
				grid-template-columns: repeat(3, minmax(0, 1fr));
				gap: 10px;
				margin-bottom: 14px;
			}
			.kpi-preview-stat {
				border: 1px solid #d7e7f7;
				background: #f4f9ff;
				border-radius: 8px;
				padding: 10px 12px;
			}
			.kpi-preview-stat-label {
				color: #5b6b80;
				font-size: 11px;
				font-weight: 700;
				text-transform: uppercase;
			}
			.kpi-preview-stat-value {
				color: #005aa8;
				font-size: 20px;
				font-weight: 800;
				line-height: 1.2;
				margin-top: 3px;
			}
			.kpi-preview-group {
				border: 1px solid #d7e7f7;
				border-radius: 8px;
				margin-bottom: 12px;
				overflow: hidden;
			}
			.kpi-preview-group-head {
				background: #005aa8;
				color: #fff;
				display: flex;
				justify-content: space-between;
				gap: 12px;
				padding: 10px 12px;
				font-weight: 800;
			}
			.kpi-preview-card {
				border-top: 1px solid #e6eef7;
				padding: 12px;
				background: #fff;
			}
			.kpi-preview-card:nth-child(even) {
				background: #f8fbff;
			}
			.kpi-preview-title {
				display: flex;
				align-items: flex-start;
				justify-content: space-between;
				gap: 14px;
				margin-bottom: 10px;
			}
			.kpi-preview-objective {
				color: #1f2937;
				font-size: 14px;
				font-weight: 800;
				overflow-wrap: anywhere;
			}
			.kpi-preview-weight {
				background: #e7f1fb;
				border: 1px solid #bfd9f2;
				border-radius: 999px;
				color: #005aa8;
				font-size: 12px;
				font-weight: 800;
				padding: 4px 10px;
				white-space: nowrap;
			}
			.kpi-preview-grid {
				display: grid;
				grid-template-columns: repeat(2, minmax(0, 1fr));
				gap: 10px;
			}
			.kpi-preview-field {
				min-width: 0;
			}
			.kpi-preview-label {
				color: #64748b;
				font-size: 10px;
				font-weight: 800;
				text-transform: uppercase;
				margin-bottom: 3px;
			}
			.kpi-preview-value {
				color: #243447;
				font-size: 12px;
				line-height: 1.45;
				white-space: normal;
				overflow-wrap: anywhere;
			}
			.kpi-preview-target {
				color: #007a3d;
				font-weight: 800;
			}
			@media (max-width: 768px) {
				.kpi-preview-summary,
				.kpi-preview-grid {
					grid-template-columns: 1fr;
				}
			}
		</style>
	`;

	const summary = `
		<div class="kpi-preview-summary">
			<div class="kpi-preview-stat">
				<div class="kpi-preview-stat-label">${__("Designation")}</div>
				<div class="kpi-preview-stat-value">${escape_html(frm.doc.designation || "-")}</div>
			</div>
			<div class="kpi-preview-stat">
				<div class="kpi-preview-stat-label">${__("Components")}</div>
				<div class="kpi-preview-stat-value">${components.length}</div>
			</div>
			<div class="kpi-preview-stat">
				<div class="kpi-preview-stat-label">${__("Total Weight")}</div>
				<div class="kpi-preview-stat-value">${format_number(total_weight)}%</div>
			</div>
		</div>
	`;

	const groups = Object.keys(grouped)
		.map((perspective) => {
			const rows = grouped[perspective];
			const group_weight = rows.reduce((sum, row) => sum + flt(row.weight), 0);
			const cards = rows.map((row) => get_component_card_html(row)).join("");
			return `
				<div class="kpi-preview-group">
					<div class="kpi-preview-group-head">
						<span>${escape_html(perspective)}</span>
						<span>${format_number(group_weight)}%</span>
					</div>
					${cards}
				</div>
			`;
		})
		.join("");

	return `${css}<div class="kpi-preview-wrap">${summary}${groups}</div>`;
}

function get_component_card_html(row) {
	return `
		<div class="kpi-preview-card">
			<div class="kpi-preview-title">
				<div class="kpi-preview-objective">${escape_html(row.objective || row.kpi_component || "-")}</div>
				<div class="kpi-preview-weight">${format_number(row.weight)}%</div>
			</div>
			<div class="kpi-preview-grid">
				${preview_field(__("Metric / Measure"), row.metric)}
				${preview_field(__("Indicator"), row.indicator)}
				${preview_field(__("Target"), row.target_display, "kpi-preview-target")}
				${preview_field(__("Evidence Required"), row.evidence_required ? __("Yes") : __("No"))}
			</div>
		</div>
	`;
}

function preview_field(label, value, value_class = "") {
	return `
		<div class="kpi-preview-field">
			<div class="kpi-preview-label">${escape_html(label)}</div>
			<div class="kpi-preview-value ${value_class}">${escape_html(value || "-")}</div>
		</div>
	`;
}

function escape_html(value) {
	return frappe.utils.escape_html(String(value == null ? "" : value));
}

function format_number(value) {
	return flt(value, 2).toLocaleString(undefined, { maximumFractionDigits: 2 });
}

function update_employee_names(dialog) {
	const rows = dialog.get_value("employees") || [];
	rows.forEach((row) => {
		if (!row.employee || row.employee_name) {
			return;
		}
		frappe.db.get_value("Employee", row.employee, "employee_name").then((response) => {
			row.employee_name = response.message ? response.message.employee_name : "";
			dialog.fields_dict.employees.grid.refresh();
		});
	});
}

function show_bulk_assignment_result(result) {
	const created = result.created || [];
	const skipped = result.skipped || [];
	const failed = result.failed || [];

	const lines = [
		`<p><b>${__("Created")}:</b> ${created.length}</p>`,
		`<p><b>${__("Skipped")}:</b> ${skipped.length}</p>`,
		`<p><b>${__("Failed")}:</b> ${failed.length}</p>`,
	];

	if (created.length) {
		lines.push(`<hr><b>${__("Created Assignments")}</b>`);
		lines.push(
			`<ul>${created
				.map((row) => `<li>${frappe.utils.escape_html(row.employee)}: ${frappe.utils.escape_html(row.assignment)}</li>`)
				.join("")}</ul>`
		);
	}

	if (skipped.length) {
		lines.push(`<hr><b>${__("Skipped")}</b>`);
		lines.push(
			`<ul>${skipped
				.map((row) => `<li>${frappe.utils.escape_html(row.employee)}: ${frappe.utils.escape_html(row.reason)}</li>`)
				.join("")}</ul>`
		);
	}

	if (failed.length) {
		lines.push(`<hr><b>${__("Failed")}</b>`);
		lines.push(
			`<ul>${failed
				.map((row) => `<li>${frappe.utils.escape_html(row.employee)}: ${frappe.utils.escape_html(row.reason)}</li>`)
				.join("")}</ul>`
		);
	}

	frappe.msgprint({
		title: __("Bulk Assignment Result"),
		indicator: failed.length ? "orange" : "green",
		message: lines.join(""),
	});
}
