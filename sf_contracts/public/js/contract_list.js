window.sfContractLifecycleColors = window.sfContractLifecycleColors || {
	Pending: "orange",
	Active: "green",
	Expired: "red",
	Completed: "blue",
	Terminated: "red",
};

frappe.listview_settings["Contract"] = {
	get_indicator(doc) {
		const status = doc.sf_contract_lifecycle_status || "Pending";
		const color = window.sfContractLifecycleColors[status] || "gray";

		return [__(status), color, `sf_contract_lifecycle_status,=,${status}`];
	},
};
