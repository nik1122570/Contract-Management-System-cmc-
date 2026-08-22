frappe.ui.form.on("KPI Review", {
	refresh(frm) {
		frm.trigger("set_primary_actions");
	},

	set_primary_actions(frm) {
		if (frm.is_new() || frm.doc.docstatus === 2) {
			return;
		}

		if (frm.doc.workflow_status === "Pending Self Rating") {
			frm.add_custom_button(__("Submit Self Rating"), () => {
				frm.call("self_submit").then(() => frm.reload_doc());
			});
		}

		if (frm.doc.workflow_status === "Pending Final Rating") {
			frm.add_custom_button(__("Complete Final Review"), () => {
				frm.call("complete_review").then(() => frm.reload_doc());
			});
			frm.add_custom_button(__("Return to Employee"), () => {
				frappe.prompt(
					[{ fieldname: "reason", fieldtype: "Small Text", label: __("Reason"), reqd: 1 }],
					(values) => frm.call("return_to_employee", { reason: values.reason }).then(() => frm.reload_doc()),
					__("Return KPI Review")
				);
			});
		}
	},
});

