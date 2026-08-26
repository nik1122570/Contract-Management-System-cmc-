window.sfContractLifecycleColors = window.sfContractLifecycleColors || {
	Active: "green",
	Expired: "red",
	Terminated: "red",
};

function setSubmittedForSigningOnDraft(frm) {
	if (frm.doc.docstatus === 0 && frm.fields_dict.submitted_for_signing && !frm.doc.submitted_for_signing) {
		frm.set_value("submitted_for_signing", 1);
	}
}

frappe.ui.form.on("Contract", {
	setup(frm) {
		setSubmittedForSigningOnDraft(frm);
	},

	refresh(frm) {
		setSubmittedForSigningOnDraft(frm);

		if (frm.doc.sf_compliance_tracker) {
			frm.add_custom_button(__("Open Compliance Tracker"), () => {
				frappe.set_route("Form", "Contract Compliance Tracker", frm.doc.sf_compliance_tracker);
			});
		}
	},

	is_signed(frm) {
		if (frm.doc.is_signed && !frm.doc.sf_signed_contract_document) {
			frappe.msgprint({
				title: __("Signed Contract Document Required"),
				message: __(
					"Attach the signed contract file in Signed Contract Document before marking this Contract as signed."
				),
				indicator: "orange",
			});
			frm.set_value("is_signed", 0);
		}
	},
});
