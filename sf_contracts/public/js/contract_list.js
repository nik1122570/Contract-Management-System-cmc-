window.sfContractLifecycleColors = window.sfContractLifecycleColors || {
	Active: "green",
	Expired: "red",
	Terminated: "red",
};

frappe.listview_settings["Contract"] = {
	add_fields: ["sf_contract_lifecycle_status", "workflow_state", "company", "sf_contract_type"],
	hide_name_column: true,

	get_indicator(doc) {
		const status = doc.sf_contract_lifecycle_status || "Active";
		const color = window.sfContractLifecycleColors[status] || "gray";

		return [__(status), color, `sf_contract_lifecycle_status,=,${status}`];
	},
};
