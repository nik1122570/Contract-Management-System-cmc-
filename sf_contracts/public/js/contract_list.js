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
	add_fields: ["sf_contract_health_score"],

	get_indicator(doc) {
		const status = doc.sf_contract_lifecycle_status || "Draft";
		const color = window.sfContractLifecycleColors[status] || "gray";

		return [__(status), color, `sf_contract_lifecycle_status,=,${status}`];
	},

	formatters: {
		sf_contract_health_score(value) {
			const score = value || "Attention Needed";
			const status_class = {
				Healthy: "healthy",
				"Attention Needed": "attention",
				Critical: "critical",
			}[score] || "attention";

			inject_contract_health_list_styles();

			return `<span class="sf-contract-health-badge ${status_class}">
				${frappe.utils.escape_html(__(score))}
			</span>`;
		},
	},
};

function inject_contract_health_list_styles() {
	if (document.getElementById("sf-contract-health-list-styles")) {
		return;
	}

	const style = document.createElement("style");
	style.id = "sf-contract-health-list-styles";
	style.textContent = `
		.sf-contract-health-badge {
			display: inline-flex;
			align-items: center;
			justify-content: center;
			min-height: 24px;
			padding: 3px 10px;
			border-radius: 999px;
			font-size: 12px;
			font-weight: 800;
			letter-spacing: 0;
			border: 1px solid transparent;
			white-space: nowrap;
		}

		.sf-contract-health-badge.healthy {
			color: #067647;
			background: #dcfae6;
			border-color: #abefc6;
		}

		.sf-contract-health-badge.attention {
			color: #b54708;
			background: #fef0c7;
			border-color: #fedf89;
		}

		.sf-contract-health-badge.critical {
			color: #b42318;
			background: #fee4e2;
			border-color: #fecdca;
		}
	`;
	document.head.appendChild(style);
}
