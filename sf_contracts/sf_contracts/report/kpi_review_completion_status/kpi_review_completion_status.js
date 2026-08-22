frappe.query_reports["KPI Review Completion Status"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
		},
		{
			fieldname: "department",
			label: __("Department"),
			fieldtype: "Link",
			options: "Department",
		},
		{
			fieldname: "designation",
			label: __("Designation"),
			fieldtype: "Link",
			options: "Designation",
		},
		{
			fieldname: "period_key",
			label: __("Period"),
			fieldtype: "Data",
		},
		{
			fieldname: "workflow_status",
			label: __("Workflow Status"),
			fieldtype: "Select",
			options: "\nPending Self Rating\nPending Final Rating\nCompleted\nCancelled",
		},
	],
};

