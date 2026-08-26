window.sfContractLifecycleColors = window.sfContractLifecycleColors || {
	Active: "green",
	Expired: "red",
	Terminated: "red",
};

if (!frappe._sf_contract_original_has_indicator) {
	frappe._sf_contract_original_has_indicator = frappe.has_indicator;
	frappe.has_indicator = function (doctype) {
		if (doctype === "Contract") {
			return false;
		}
		return frappe._sf_contract_original_has_indicator.apply(this, arguments);
	};
}

frappe.listview_settings["Contract"] = {
	add_fields: ["party_name", "workflow_state", "company", "sf_contract_lifecycle_status"],
	hide_name_column: true,
};
