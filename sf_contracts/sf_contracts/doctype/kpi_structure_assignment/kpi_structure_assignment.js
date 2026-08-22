frappe.ui.form.on("KPI Structure Assignment", {
	refresh(frm) {
		if (frm.doc.docstatus === 1 && frm.doc.status === "Active") {
			frm.add_custom_button(__("Create Due Reviews"), () => {
				frappe.call({
					method: "sf_contracts.kpi_management.create_due_reviews",
					args: { assignment: frm.doc.name },
					freeze: true,
					callback: () => frm.reload_doc(),
				});
			});
		}
	},
});

