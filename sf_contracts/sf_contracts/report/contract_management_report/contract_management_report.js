frappe.query_reports["Contract Management Report"] = {
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
			fieldname: "lifecycle_status",
			label: __("Lifecycle Status"),
			fieldtype: "Select",
			options: "\nActive\nExpired\nTerminated",
		},
		{
			fieldname: "health_score",
			label: __("Contract Health"),
			fieldtype: "Select",
			options: "\nHealthy\nAttention Needed\nCritical",
		},
		{
			fieldname: "party_type",
			label: __("Party Type"),
			fieldtype: "Link",
			options: "DocType",
			get_query: () => ({
				filters: {
					name: ["in", ["Customer", "Supplier", "Employee", "Shareholder"]],
				},
			}),
		},
		{
			fieldname: "party_name",
			label: __("Party Name"),
			fieldtype: "Data",
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "SF Companies",
		},
		{
			fieldname: "contract_type",
			label: __("Contract Type"),
			fieldtype: "Link",
			options: "Contract Type",
		},
		{
			fieldname: "from_date",
			label: __("Start From"),
			fieldtype: "Date",
		},
		{
			fieldname: "to_date",
			label: __("End To"),
			fieldtype: "Date",
		},
		{
			fieldname: "expiry_within_days",
			label: __("Expiring Within Days"),
			fieldtype: "Int",
		},
	],
};
