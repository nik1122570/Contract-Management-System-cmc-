frappe.query_reports["Overdue KPI Reviews"] = {
	filters: [
		{
			fieldname: "overdue_stage",
			label: __("Overdue Stage"),
			fieldtype: "Select",
			options: "\nSelf Rating\nFinal Rating",
		},
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
	],
};

