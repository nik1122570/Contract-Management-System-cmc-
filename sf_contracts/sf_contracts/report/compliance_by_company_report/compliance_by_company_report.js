frappe.query_reports["Compliance by Company Report"] = {
	filters: [
		{
			fieldname: "report_view",
			label: __("Report View"),
			fieldtype: "Select",
			options: "Detailed List\nSummary List",
			default: "Detailed List",
			reqd: 1,
		},
		{
			fieldname: "company",
			label: __("SF Company"),
			fieldtype: "Link",
			options: "SF Companies",
		},
		{
			fieldname: "party_name",
			label: __("Entity / Company Name"),
			fieldtype: "Data",
		},
		{
			fieldname: "compliance_category",
			label: __("Compliance Category"),
			fieldtype: "Link",
			options: "Compliance Category",
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: "\nCompliant\nPending\nNot Compliant\nPaid\nNot Paid\nActive\nExpired\nApproved\nNot Approved\nN/A\nIn Progress",
		},
		{
			fieldname: "priority",
			label: __("Priority"),
			fieldtype: "Select",
			options: "\nLow\nMedium\nHigh\nCritical",
		},
		{
			fieldname: "due_from",
			label: __("Due From"),
			fieldtype: "Date",
		},
		{
			fieldname: "due_to",
			label: __("Due To"),
			fieldtype: "Date",
		},
		{
			fieldname: "expiry_from",
			label: __("Expiry From"),
			fieldtype: "Date",
		},
		{
			fieldname: "expiry_to",
			label: __("Expiry To"),
			fieldtype: "Date",
		},
		{
			fieldname: "expiry_within_days",
			label: __("Expiring Within Days"),
			fieldtype: "Int",
		},
	],
};
