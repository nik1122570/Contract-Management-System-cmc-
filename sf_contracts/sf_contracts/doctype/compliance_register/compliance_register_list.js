frappe.listview_settings["Compliance Register"] = {
	hide_name_column: true,
	add_fields: ["status", "priority"],

	get_indicator(doc) {
		if (doc.priority === "Critical" || doc.status === "Expired" || doc.status === "Not Compliant") {
			return [__("Critical"), "red", "priority,=,Critical"];
		}

		if (doc.priority === "High") {
			return [__("High Priority"), "orange", "priority,=,High"];
		}

		if (doc.status === "Compliant" || doc.status === "Active" || doc.status === "Paid") {
			return [__(doc.status), "green", `status,=,${doc.status}`];
		}

		return [__(doc.status || "Pending"), "gray", `status,=,${doc.status || "Pending"}`];
	},
};
