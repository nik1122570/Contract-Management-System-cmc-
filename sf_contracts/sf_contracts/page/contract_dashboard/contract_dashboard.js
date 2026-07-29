frappe.pages["contract-dashboard"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Contract Dashboard"),
		single_column: true,
	});

	frappe.breadcrumbs.add("SF Contracts");
	wrapper.contract_dashboard = new sf_contracts.ContractDashboard(wrapper);
};

frappe.provide("sf_contracts");

sf_contracts.ContractDashboard = class ContractDashboard {
	constructor(wrapper) {
		this.wrapper = wrapper;
		this.page = wrapper.page;
		this.$main = $(wrapper).find(".layout-main-section");
		this.active_status = null;

		this.setup();
		this.refresh();
	}

	setup() {
		this.page.set_primary_action(__("Refresh"), () => this.refresh(), "fa fa-refresh");

		this.$main.empty().append(`
			<div class="sf-contract-dashboard">
				<div class="sf-contract-dashboard__hero">
					<div class="sf-contract-dashboard__brand">
						<div class="sf-contract-dashboard__logo" aria-hidden="true">
							<span></span><span></span><span></span><span></span><span></span>
							<span></span><span></span><span></span><span></span><span></span>
						</div>
						<div>
							<div class="sf-contract-dashboard__eyebrow">${__("SF Group of Companies Ltd")}</div>
							<div class="sf-contract-dashboard__title">${__("Contract Management Dashboard")}</div>
							<div class="sf-contract-dashboard__subtitle">
								${__("Monitor contract status, execution delays, expiry risk, and pending action from one control view.")}
							</div>
						</div>
					</div>
					<div class="sf-contract-dashboard__hero-action">
						<button class="btn btn-default btn-sm" data-contract-list>
							<i class="fa fa-list"></i> ${__("Contract List")}
						</button>
						<button class="btn btn-primary btn-sm" data-new-contract>
							<i class="fa fa-plus"></i> ${__("New Contract")}
						</button>
					</div>
				</div>
				<div class="sf-contract-dashboard__summary"></div>
				<div class="sf-contract-dashboard__expanded"></div>
				<div class="sf-contract-dashboard__grid">
					<div class="sf-contract-dashboard__panel">
						<div class="sf-contract-dashboard__panel-title">${__("Lifecycle Predictor")}</div>
						<div class="sf-contract-dashboard__predictor"></div>
					</div>
					<div class="sf-contract-dashboard__panel">
						<div class="sf-contract-dashboard__panel-title">${__("Contracts Near Expiration")}</div>
						<div data-watchlist="expiring_soon"></div>
					</div>
					<div class="sf-contract-dashboard__panel">
						<div class="sf-contract-dashboard__panel-title">${__("Contracts Near Completion")}</div>
						<div data-watchlist="near_completion"></div>
					</div>
					<div class="sf-contract-dashboard__panel">
						<div class="sf-contract-dashboard__panel-title">${__("Unsigned / Pending Contracts")}</div>
						<div data-watchlist="unsigned_pending"></div>
					</div>
				</div>
			</div>
		`);

		this.$main.find("[data-new-contract]").on("click", () => frappe.new_doc("Contract"));
		this.$main.find("[data-contract-list]").on("click", () => frappe.set_route("List", "Contract"));
	}

	refresh() {
		frappe.call({
			method: "sf_contracts.dashboard.get_contract_dashboard",
			freeze: true,
			freeze_message: __("Loading Contract Dashboard"),
			callback: (response) => {
				this.data = response.message || {};
				this.render();
			},
		});
	}

	render() {
		this.render_cards(this.data.cards || []);
		this.render_predictor(this.data.predictor || []);
		this.render_watchlists(this.data.watchlists || {});
		this.render_expanded_status(this.active_status || (this.data.cards || [])[0]?.status);
	}

	render_cards(cards) {
		const $summary = this.$main.find(".sf-contract-dashboard__summary");
		$summary.empty();

		cards.forEach((card) => {
			const active_class = card.status === this.active_status ? " is-active" : "";
			const $card = $(`
				<button class="sf-contract-card${active_class}" data-status="${frappe.utils.escape_html(card.status)}">
					<span class="sf-contract-card__label">${frappe.utils.escape_html(card.label)}</span>
					<span class="sf-contract-card__count text-${card.color}">${card.count}</span>
					<span class="sf-contract-card__action">
						<i class="fa fa-chevron-down"></i>
					</span>
				</button>
			`);

			$card.on("click", () => {
				this.active_status = this.active_status === card.status ? null : card.status;
				this.render_cards(cards);
				this.render_expanded_status(this.active_status || card.status);
			});

			$summary.append($card);
		});
	}

	render_expanded_status(status) {
		const cards = this.data.cards || [];
		const card = cards.find((item) => item.status === status);
		const $expanded = this.$main.find(".sf-contract-dashboard__expanded");

		if (!card) {
			$expanded.empty();
			return;
		}

		$expanded.html(`
			<div class="sf-contract-dashboard__panel">
				<div class="sf-contract-dashboard__panel-header">
					<div>
						<div class="sf-contract-dashboard__panel-title">${frappe.utils.escape_html(card.label)}</div>
						<div class="text-muted">${__("Click a row to open the Contract record.")}</div>
					</div>
					<button class="btn btn-default btn-sm" data-view-status="${frappe.utils.escape_html(card.status)}">
						${__("View All")}
					</button>
				</div>
				<div class="sf-contract-list"></div>
			</div>
		`);

		$expanded.find("[data-view-status]").on("click", () => this.open_filtered_list(card.status));
		this.render_contract_list($expanded.find(".sf-contract-list"), card.contracts || [], {
			empty_message: __("No contracts found for this status."),
		});
	}

	render_predictor(items) {
		const $predictor = this.$main.find(".sf-contract-dashboard__predictor");
		$predictor.empty();

		items.forEach((item) => {
			$predictor.append(`
				<div class="sf-contract-predictor-row">
					<span class="indicator ${item.indicator}"></span>
					<span>${frappe.utils.escape_html(item.label)}</span>
					<strong>${item.value}</strong>
				</div>
			`);
		});
	}

	render_watchlists(watchlists) {
		this.render_contract_list(this.$main.find('[data-watchlist="expiring_soon"]'), watchlists.expiring_soon || [], {
			empty_message: __("No active contracts expiring in the next 90 days."),
			show_days: __("days left"),
		});
		this.render_contract_list(this.$main.find('[data-watchlist="near_completion"]'), watchlists.near_completion || [], {
			empty_message: __("No active contracts ending in the next 30 days."),
			show_days: __("days left"),
		});
		this.render_contract_list(this.$main.find('[data-watchlist="unsigned_pending"]'), watchlists.unsigned_pending || [], {
			empty_message: __("No unsigned pending contracts."),
			show_days_open: __("days pending"),
		});
	}

	render_contract_list($target, contracts, options = {}) {
		$target.empty();

		if (!contracts.length) {
			$target.append(`<div class="sf-contract-empty">${options.empty_message || __("No contracts found.")}</div>`);
			return;
		}

		contracts.forEach((contract) => {
			const days_text = this.get_days_text(contract, options);
			const $row = $(`
				<button class="sf-contract-row" data-contract="${frappe.utils.escape_html(contract.name)}">
					<span class="sf-contract-row__main">
						<strong>${frappe.utils.escape_html(contract.party || contract.name)}</strong>
						<span class="text-muted">${frappe.utils.escape_html(contract.name)}</span>
					</span>
					<span class="sf-contract-row__meta">
						<span class="indicator ${contract.status_color || "gray"}">${frappe.utils.escape_html(
							contract.lifecycle_status || ""
						)}</span>
						${days_text ? `<span>${days_text}</span>` : ""}
					</span>
				</button>
			`);

			$row.on("click", () => frappe.set_route("Form", "Contract", contract.name));
			$target.append($row);
		});
	}

	get_days_text(contract, options) {
		if (options.show_days && contract.days_to_end !== null && contract.days_to_end !== undefined) {
			return `${contract.days_to_end} ${options.show_days}`;
		}

		if (options.show_days_open && contract.days_open !== null && contract.days_open !== undefined) {
			return `${contract.days_open} ${options.show_days_open}`;
		}

		return "";
	}

	open_filtered_list(status) {
		frappe.route_options = {
			sf_contract_lifecycle_status: status,
		};
		frappe.set_route("List", "Contract");
	}
};
