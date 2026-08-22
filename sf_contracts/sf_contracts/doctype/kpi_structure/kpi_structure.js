frappe.ui.form.on("KPI Structure", {
	refresh(frm) {
		update_total_weight(frm);
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

