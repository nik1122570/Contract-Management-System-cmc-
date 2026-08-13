frappe.ui.form.on("Compliance Register", {
	refresh(frm) {
		apply_category_rules(frm);
		add_category_buttons(frm);
	},

	compliance_category(frm) {
		apply_category_rules(frm);
		populate_category_details(frm);
	},

	company(frm) {
		if (frm.doc.company) {
			frappe.db.get_value("SF Companies", frm.doc.company, "company_name").then(({ message }) => {
				if (message?.company_name) {
					frm.set_value("party_name", message.company_name);
				}
			});
		}
	},

	expiry_date(frm) {
		set_days_to_expiry(frm);
	},

	due_date(frm) {
		set_days_to_expiry(frm);
	},
});

const managed_common_fields = [
	"authority",
	"registration_or_license_no",
	"period",
	"month",
	"year",
	"issue_date",
	"effective_date",
	"due_date",
	"expiry_date",
	"amount",
	"attachment",
];

const requirement_map = {
	authority: "requires_authority",
	registration_or_license_no: "requires_license_no",
	period: "requires_period",
	month: "requires_month_year",
	year: "requires_month_year",
	issue_date: "requires_issue_date",
	effective_date: "requires_effective_date",
	due_date: "requires_due_date",
	expiry_date: "requires_expiry_date",
	amount: "requires_amount",
	attachment: "requires_attachment",
};

function add_category_buttons(frm) {
	if (!frm.doc.compliance_category) {
		return;
	}

	frm.add_custom_button(__("Open Category"), () => {
		frappe.set_route("Form", "Compliance Category", frm.doc.compliance_category);
	});
}

function apply_category_rules(frm) {
	if (!frm.doc.compliance_category) {
		managed_common_fields.forEach((fieldname) => {
			frm.toggle_display(fieldname, true);
			frm.toggle_reqd(fieldname, false);
		});
		return;
	}

	frappe.db.get_doc("Compliance Category", frm.doc.compliance_category).then((category) => {
		managed_common_fields.forEach((fieldname) => {
			const required = Boolean(category[requirement_map[fieldname]]);
			frm.toggle_display(fieldname, required);
			frm.toggle_reqd(fieldname, required);
		});

		frm.refresh_fields();
	});
}

function populate_category_details(frm) {
	if (!frm.doc.compliance_category) {
		return;
	}

	frappe.db.get_doc("Compliance Category", frm.doc.compliance_category).then((category) => {
		const existing = {};
		(frm.doc.details || []).forEach((row) => {
			if (row.field_key) {
				existing[row.field_key] = row;
			}
		});

		(category.fields || []).forEach((field) => {
			if (!field.field_key) {
				return;
			}

			let row = existing[field.field_key];
			if (!row) {
				row = frm.add_child("details");
			}

			row.field_label = field.field_label;
			row.field_key = field.field_key;
			row.field_type = field.field_type;
			row.is_required = field.is_required;

			if (!row.field_value && field.default_value) {
				row.field_value = field.default_value;
			}
		});

		frm.refresh_field("details");
	});
}

function set_days_to_expiry(frm) {
	const date_value = frm.doc.expiry_date || frm.doc.due_date;
	if (!date_value) {
		frm.set_value("days_to_expiry", null);
		return;
	}

	const today = frappe.datetime.get_today();
	frm.set_value("days_to_expiry", frappe.datetime.get_day_diff(date_value, today));
}
