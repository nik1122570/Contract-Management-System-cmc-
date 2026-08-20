frappe.listview_settings["Contract Compliance Tracker"] = {
	add_fields: ["contract", "company", "party_name", "contract_type", "compliance_percentage"],
	hide_name_column: true,

	formatters: {
		compliance_percentage(value) {
			const percentage = cint(value || 0);
			let status_class = "pending";

			if (percentage >= 100) {
				status_class = "compliant";
			} else if (percentage > 0) {
				status_class = "partial";
			}

			inject_compliance_list_styles();

			return `<span class="sf-compliance-list-badge ${status_class}">
				${frappe.utils.escape_html(`${percentage}%`)}
			</span>`;
		},
	},
};

function inject_compliance_list_styles() {
	if (document.getElementById("sf-compliance-list-styles")) {
		return;
	}

	const style = document.createElement("style");
	style.id = "sf-compliance-list-styles";
	style.textContent = `
		.sf-compliance-list-badge {
			display: inline-flex;
			align-items: center;
			justify-content: center;
			min-width: 54px;
			min-height: 24px;
			padding: 3px 9px;
			border-radius: 999px;
			font-size: 12px;
			font-weight: 800;
			letter-spacing: 0;
			border: 1px solid transparent;
		}

		.sf-compliance-list-badge.compliant {
			color: #067647;
			background: #dcfae6;
			border-color: #abefc6;
		}

		.sf-compliance-list-badge.partial {
			color: #b54708;
			background: #fef0c7;
			border-color: #fedf89;
		}

		.sf-compliance-list-badge.pending {
			color: #475467;
			background: #f2f4f7;
			border-color: #eaecf0;
		}
	`;
	document.head.appendChild(style);
}
