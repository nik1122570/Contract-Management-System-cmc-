frappe.ui.form.on("KPI Structure", {
	refresh(frm) {
		update_total_weight(frm);
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
