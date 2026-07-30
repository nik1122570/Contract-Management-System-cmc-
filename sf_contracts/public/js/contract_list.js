window.sfContractLifecycleColors = window.sfContractLifecycleColors || {
	Draft: "gray",
	"Pending Execution": "orange",
	"Executed – Awaiting Commencement": "blue",
	Active: "green",
	"Expired – Services Continuing": "red",
	Closed: "blue",
	Terminated: "red",
};

frappe.listview_settings["Contract"] = {
	get_indicator(doc) {
		const status = doc.sf_contract_lifecycle_status || "Draft";
		const color = window.sfContractLifecycleColors[status] || "gray";

		return [__(status), color, `sf_contract_lifecycle_status,=,${status}`];
	},
};
