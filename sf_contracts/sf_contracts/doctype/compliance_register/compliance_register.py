# Copyright (c) 2026, Nickson John and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, getdate, nowdate


COMMON_CATEGORY_REQUIREMENT_MAP = {
	"authority": "requires_authority",
	"registration_or_license_no": "requires_license_no",
	"period": "requires_period",
	"month": "requires_month_year",
	"year": "requires_month_year",
	"issue_date": "requires_issue_date",
	"effective_date": "requires_effective_date",
	"due_date": "requires_due_date",
	"expiry_date": "requires_expiry_date",
	"amount": "requires_amount",
	"attachment": "requires_attachment",
}

DEFAULT_PRIORITY_THRESHOLDS = {
	"critical_days": 7,
	"high_days": 30,
	"medium_days": 90,
}


class ComplianceRegister(Document):
	def validate(self):
		self.set_party_from_company()
		self.sync_category_detail_rows()
		self.validate_required_common_fields()
		self.validate_required_detail_rows()
		self.set_days_to_expiry()
		self.set_priority()

	def set_party_from_company(self):
		if self.company and not self.party_name:
			self.party_name = frappe.db.get_value("SF Companies", self.company, "company_name") or self.company

	def get_category_doc(self):
		if not self.compliance_category:
			return None

		return frappe.get_cached_doc("Compliance Category", self.compliance_category)

	def sync_category_detail_rows(self):
		category = self.get_category_doc()
		if not category:
			return

		existing_by_key = {row.field_key: row for row in self.details if row.field_key}

		for field in category.fields:
			if not field.field_key:
				continue

			row = existing_by_key.get(field.field_key)
			if not row:
				row = self.append("details", {})

			row.field_label = field.field_label
			row.field_key = field.field_key
			row.field_type = field.field_type
			row.is_required = field.is_required

			if not row.field_value and field.default_value:
				row.field_value = field.default_value

	def validate_required_common_fields(self):
		category = self.get_category_doc()
		if not category:
			return

		missing = []
		for fieldname, requirement_flag in COMMON_CATEGORY_REQUIREMENT_MAP.items():
			if category.get(requirement_flag) and not self.get(fieldname):
				missing.append(frappe.bold(self.meta.get_label(fieldname)))

		if missing:
			frappe.throw(
				_("Please fill the required fields for {0}: {1}").format(
					frappe.bold(self.compliance_category),
					", ".join(missing),
				),
				title=_("Missing Compliance Fields"),
			)

	def validate_required_detail_rows(self):
		missing = [
			frappe.bold(row.field_label)
			for row in self.details
			if row.is_required and not (row.field_value or "").strip()
		]

		if missing:
			frappe.throw(
				_("Please fill the required category-specific fields: {0}").format(", ".join(missing)),
				title=_("Missing Compliance Details"),
			)

	def set_days_to_expiry(self):
		target_date = self.expiry_date or self.due_date
		self.days_to_expiry = date_diff(getdate(target_date), getdate(nowdate())) if target_date else None

	def set_priority(self):
		normalized_status = (self.status or "").strip().lower()

		if normalized_status in ("expired", "not compliant", "not paid"):
			self.priority = "Critical"
			return

		thresholds = get_priority_thresholds()

		if self.days_to_expiry is None:
			self.priority = "Low"
		elif self.days_to_expiry < 0:
			self.priority = "Critical"
		elif self.days_to_expiry <= thresholds["critical_days"]:
			self.priority = "Critical"
		elif self.days_to_expiry <= thresholds["high_days"]:
			self.priority = "High"
		elif self.days_to_expiry <= thresholds["medium_days"]:
			self.priority = "Medium"
		else:
			self.priority = "Low"


def get_priority_thresholds():
	thresholds = DEFAULT_PRIORITY_THRESHOLDS.copy()

	if frappe.db.exists("DocType", "Compliance Settings"):
		settings = frappe.get_single("Compliance Settings")
		for fieldname, default_value in DEFAULT_PRIORITY_THRESHOLDS.items():
			thresholds[fieldname] = settings.get(fieldname) or default_value

	thresholds = {key: max(0, int(value)) for key, value in thresholds.items()}
	thresholds["high_days"] = max(thresholds["high_days"], thresholds["critical_days"])
	thresholds["medium_days"] = max(thresholds["medium_days"], thresholds["high_days"])

	return thresholds
