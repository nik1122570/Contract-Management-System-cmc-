import frappe
from frappe import _
from frappe.model.document import Document


class KPIComponent(Document):
	def validate(self):
		self.objective = (self.objective or "").strip()
		if self.default_target_operator == "Range":
			if self.default_target_value is None or self.default_target_value_2 is None:
				frappe.throw(_("Both target values are required when the target operator is Range."))
			if self.default_target_value_2 <= self.default_target_value:
				frappe.throw(_("Default Target Value 2 must be greater than Default Target Value."))

		if self.status == "Active":
			self.validate_activation_fields()
			self.validate_scoring_bands()

	def validate_activation_fields(self):
		required_fields = {
			"objective": _("Objective"),
			"metric": _("Metric / Measure"),
			"indicator": _("Indicator"),
			"perspective": _("Perspective"),
			"result_data_type": _("Result Data Type"),
			"measurement_direction": _("Measurement Direction"),
			"scoring_method": _("Scoring Method"),
			"data_source": _("Data Source"),
		}
		missing = [label for fieldname, label in required_fields.items() if not self.get(fieldname)]
		if missing:
			frappe.throw(_("Cannot activate KPI Component. Missing: {0}").format(", ".join(missing)))

	def validate_scoring_bands(self):
		if self.scoring_method != "Threshold Bands":
			return
		if not self.scoring_bands:
			frappe.throw(_("Scoring Bands are required when Scoring Method is Threshold Bands."))

		ranges = []
		for row in self.scoring_bands:
			if row.score_percentage is None or row.score_percentage < 0 or row.score_percentage > 100:
				frappe.throw(_("Row {0}: Score Percentage must be between 0 and 100.").format(row.idx))
			if row.condition == "Range":
				if row.from_value is None or row.to_value is None:
					frappe.throw(_("Row {0}: From Value and To Value are required for Range.").format(row.idx))
				if row.to_value <= row.from_value:
					frappe.throw(_("Row {0}: To Value must be greater than From Value.").format(row.idx))
				ranges.append((row.from_value, row.to_value, row.idx))

		for i, current in enumerate(ranges):
			for other in ranges[i + 1 :]:
				if current[0] <= other[1] and other[0] <= current[1]:
					frappe.throw(_("Scoring Band rows {0} and {1} overlap.").format(current[2], other[2]))

	def before_rename(self, olddn, newdn, merge=False):
		if frappe.db.exists("KPI Structure Item", {"kpi_component": olddn}):
			frappe.throw(_("KPI Component cannot be renamed after it has been used in a KPI Structure."))

