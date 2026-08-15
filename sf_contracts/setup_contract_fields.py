import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter


def add_signed_contract_document_field():
	"""Add signing-related fields to ERPNext Contract."""
	custom_fields = {
		"Contract": [
			{
				"fieldname": "submitted_for_signing",
				"label": "Submitted for Signing",
				"fieldtype": "Check",
				"insert_after": "sb_signee",
				"allow_on_submit": 1,
				"is_system_generated": 1,
				"no_copy": 1,
				"description": "",
			},
			{
				"fieldname": "sf_signed_contract_document",
				"label": "Signed Contract Document",
				"fieldtype": "Attach",
				"insert_after": "signed_on",
				"allow_on_submit": 1,
				"is_system_generated": 1,
				"no_copy": 1,
				"description": "",
			}
		]
	}

	create_custom_fields(custom_fields, update=True)
	frappe.clear_cache(doctype="Contract")


def add_contract_lifecycle_fields():
	"""Add Legal-facing lifecycle fields to ERPNext Contract."""
	custom_fields = {
		"Contract": [
			{
				"fieldname": "sf_contract_status_section",
				"label": "Lifecycle & Health",
				"fieldtype": "Section Break",
				"insert_after": "party_full_name",
				"allow_on_submit": 1,
				"is_system_generated": 1,
			},
			{
				"fieldname": "sf_contract_lifecycle_status",
				"label": "Contract Lifecycle Status",
				"fieldtype": "Select",
				"options": "Active\nExpired\nTerminated",
				"default": "Active",
				"insert_after": "sf_contract_status_section",
				"allow_on_submit": 1,
				"is_system_generated": 1,
				"in_list_view": 1,
				"in_standard_filter": 1,
				"no_copy": 1,
				"description": "",
			},
			{
				"fieldname": "sf_completion_date",
				"label": "Completion Date",
				"fieldtype": "Date",
				"insert_after": "sf_contract_lifecycle_status",
				"allow_on_submit": 1,
				"is_system_generated": 1,
				"depends_on": "eval:0",
				"no_copy": 1,
			},
			{
				"fieldname": "sf_contract_status_column",
				"fieldtype": "Column Break",
				"insert_after": "sf_termination_reason",
				"allow_on_submit": 1,
				"is_system_generated": 1,
			},
			{
				"fieldname": "sf_termination_date",
				"label": "Termination Date",
				"fieldtype": "Date",
				"insert_after": "sf_contract_status_column",
				"allow_on_submit": 1,
				"is_system_generated": 1,
				"depends_on": "eval:doc.sf_contract_lifecycle_status=='Terminated'",
				"no_copy": 1,
			},
			{
				"fieldname": "sf_termination_reason",
				"label": "Termination Reason",
				"fieldtype": "Small Text",
				"insert_after": "sf_termination_date",
				"allow_on_submit": 1,
				"is_system_generated": 1,
				"depends_on": "eval:doc.sf_contract_lifecycle_status=='Terminated'",
				"no_copy": 1,
			},
		]
	}

	create_custom_fields(custom_fields, update=True)
	migrate_contract_lifecycle_status_values()
	frappe.clear_cache(doctype="Contract")


def migrate_contract_lifecycle_status_values():
	"""Map old SF lifecycle values to the current Legal vocabulary."""
	if not frappe.db.has_column("Contract", "sf_contract_lifecycle_status"):
		return

	status_map = {
		"Draft": "Active",
		"Pending": "Active",
		"Pending Execution": "Active",
		"Executed – Awaiting Commencement": "Active",
		"Expired – Services Continuing": "Expired",
		"Completed": "Active",
		"Closed": "Active",
	}

	for old_status, new_status in status_map.items():
		for contract in frappe.get_all(
			"Contract",
			filters={"sf_contract_lifecycle_status": old_status},
			pluck="name",
		):
			frappe.db.set_value(
				"Contract",
				contract,
				"sf_contract_lifecycle_status",
				new_status,
				update_modified=False,
			)


def add_contract_business_fields():
	"""Add SF Group business fields used for legal contract reporting."""
	fields = []
	meta = frappe.get_meta("Contract", cached=False)

	if not meta.has_field("company"):
		fields.append(
			{
				"fieldname": "company",
				"label": "Company",
				"fieldtype": "Link",
				"options": "SF Companies",
				"insert_after": "is_signed",
				"is_system_generated": 1,
				"allow_on_submit": 1,
				"in_list_view": 1,
				"in_standard_filter": 1,
				"description": "",
			}
		)

	fields.extend(
		[
			{
				"fieldname": "sf_legal_classification_section",
				"label": "Legal Classification",
				"fieldtype": "Section Break",
				"insert_after": "party_full_name",
				"is_system_generated": 1,
				"allow_on_submit": 1,
			},
		{
			"fieldname": "sf_contractor",
			"label": "Contractor",
			"fieldtype": "Link",
			"options": "Contractor",
			"insert_after": "sf_legal_classification_section",
			"is_system_generated": 1,
			"allow_on_submit": 1,
				"in_list_view": 0,
				"in_standard_filter": 1,
				"description": "",
			},
			{
				"fieldname": "sf_legal_classification_column",
				"fieldtype": "Column Break",
				"insert_after": "sf_contractor",
				"is_system_generated": 1,
				"allow_on_submit": 1,
			},
		{
			"fieldname": "sf_contract_type",
			"label": "Contract Type",
			"fieldtype": "Link",
			"options": "Contract Type",
			"insert_after": "sf_legal_classification_column",
			"is_system_generated": 1,
			"allow_on_submit": 1,
				"in_list_view": 1,
				"in_standard_filter": 1,
				"description": "",
			},
			{
				"fieldname": "sf_subsidiary_signee",
				"label": "Subsidiary Signee",
				"fieldtype": "Data",
				"insert_after": "signee",
				"is_system_generated": 1,
				"allow_on_submit": 1,
				"description": "",
			},
		]
	)

	create_custom_fields({"Contract": fields}, update=True)
	migrate_contract_company_values()
	frappe.clear_cache(doctype="Contract")


def migrate_contract_company_values():
	"""Move values from a manually-created Company field into the stable fieldname."""
	if not frappe.db.has_column("Contract", "company"):
		return

	for source_field in get_legacy_company_fields():
		if source_field == "company" or not frappe.db.has_column("Contract", source_field):
			continue

		frappe.db.sql(
			f"""
			update `tabContract`
			set company = `{source_field}`
			where ifnull(company, '') = ''
				and ifnull(`{source_field}`, '') != ''
			"""
		)


def get_legacy_company_fields():
	meta = frappe.get_meta("Contract", cached=False)
	return [
		df.fieldname
		for df in meta.fields
		if df.fieldname
		and df.fieldtype == "Link"
		and df.options == "SF Companies"
		and (df.label or "").strip().lower() in {"company", "sf company", "entity", "entity / company"}
	]


def protect_contract_custom_fields():
	"""Mark app-managed Contract Custom Fields as system generated.

	This keeps Customize Form from trying to delete them when a non-Administrator
	user saves layout changes.
	"""
	fieldnames = (
		"submitted_for_signing",
		"sf_signed_contract_document",
		"company",
		"sf_legal_classification_section",
		"sf_contractor",
		"sf_legal_classification_column",
		"sf_contract_type",
		"sf_subsidiary_signee",
		"sf_contract_status_section",
		"sf_contract_lifecycle_status",
		"sf_completion_date",
		"sf_contract_status_column",
		"sf_termination_date",
		"sf_termination_reason",
		"sf_contract_health_score",
		"sf_contract_health_reason",
		"sf_compliance_section",
		"sf_compliance_tracker",
	)

	for custom_field in frappe.get_all(
		"Custom Field",
		filters={"dt": "Contract", "fieldname": ["in", fieldnames]},
		pluck="name",
	):
		frappe.db.set_value(
			"Custom Field",
			custom_field,
			"is_system_generated",
			1,
			update_modified=False,
		)
	frappe.clear_cache(doctype="Contract")


def add_contract_health_fields():
	"""Add a management-facing health indicator to ERPNext Contract."""
	custom_fields = {
		"Contract": [
			{
				"fieldname": "sf_contract_health_score",
				"label": "Contract Health Score",
				"fieldtype": "Select",
				"options": "Healthy\nAttention Needed\nCritical",
				"default": "Attention Needed",
				"insert_after": "sf_contract_lifecycle_status",
				"read_only": 1,
				"allow_on_submit": 1,
				"is_system_generated": 1,
				"in_list_view": 0,
				"in_standard_filter": 1,
				"no_copy": 1,
				"description": "",
			},
			{
				"fieldname": "sf_contract_health_reason",
				"label": "Contract Health Reason",
				"fieldtype": "Small Text",
				"insert_after": "sf_contract_health_score",
				"read_only": 1,
				"allow_on_submit": 1,
				"is_system_generated": 1,
				"no_copy": 1,
				"description": "",
			},
		]
	}

	create_custom_fields(custom_fields, update=True)
	frappe.clear_cache(doctype="Contract")


def add_contract_compliance_link_field():
	"""Add the Contract Compliance Tracker link to ERPNext Contract."""
	custom_fields = {
		"Contract": [
			{
				"fieldname": "sf_compliance_section",
				"label": "Contract Compliance",
				"fieldtype": "Section Break",
				"insert_after": "requires_fulfilment",
				"collapsible": 1,
				"allow_on_submit": 1,
				"is_system_generated": 1,
			},
			{
				"fieldname": "sf_compliance_tracker",
				"label": "Contract Compliance Tracker",
				"fieldtype": "Link",
				"options": "Contract Compliance Tracker",
				"insert_after": "sf_compliance_section",
				"read_only": 1,
				"allow_on_submit": 1,
				"is_system_generated": 1,
				"no_copy": 1,
				"description": "",
			},
		]
	}

	create_custom_fields(custom_fields, update=True)
	frappe.clear_cache(doctype="Contract")


def set_requires_fulfilment_always_enabled():
	"""Require every Contract to have fulfilment tracking enabled."""
	make_property_setter(
		"Contract",
		"requires_fulfilment",
		"default",
		"1",
		"Check",
	)
	make_property_setter(
		"Contract",
		"requires_fulfilment",
		"read_only",
		"1",
		"Check",
	)

	if frappe.db.has_column("Contract", "requires_fulfilment"):
		frappe.db.sql(
			"""
			update `tabContract`
			set requires_fulfilment = 1
			where ifnull(requires_fulfilment, 0) = 0
			"""
		)

	frappe.clear_cache(doctype="Contract")


def sync_contract_field_order():
	"""Keep app-added Contract fields visible when Customize Form has a saved field_order."""
	meta = frappe.get_meta("Contract", cached=False)
	field_order = [df.fieldname for df in meta.fields if df.fieldname]

	def move_after(fieldname, anchor):
		if fieldname in field_order:
			field_order.remove(fieldname)

		if anchor in field_order:
			field_order.insert(field_order.index(anchor) + 1, fieldname)
		else:
			field_order.append(fieldname)

	move_after("party_name", "party_type")
	move_after("party_user", "party_name")
	move_after("party_full_name", "party_user")
	move_after("sf_legal_classification_section", "party_full_name")
	move_after("sf_contractor", "sf_legal_classification_section")
	move_after("sf_legal_classification_column", "sf_contractor")
	move_after("sf_contract_type", "sf_legal_classification_column")
	move_after("sf_contract_status_section", "sf_contract_type")
	move_after("sf_contract_lifecycle_status", "sf_contract_status_section")
	move_after("sf_completion_date", "sf_contract_lifecycle_status")
	move_after("sf_contract_status_column", "sf_completion_date")
	move_after("sf_contract_health_score", "sf_contract_status_column")
	move_after("sf_contract_health_reason", "sf_contract_health_score")
	move_after("sf_termination_date", "sf_contract_health_reason")
	move_after("sf_termination_reason", "sf_termination_date")
	move_after("submitted_for_signing", "sb_signee")
	move_after("is_signed", "submitted_for_signing")
	move_after("company", "is_signed")
	move_after("signee", "company")
	move_after("sf_subsidiary_signee", "signee")
	move_after("signed_on", "sf_subsidiary_signee")
	move_after("sf_signed_contract_document", "signed_on")
	move_after("sf_compliance_section", "requires_fulfilment")
	move_after("sf_compliance_tracker", "sf_compliance_section")

	make_property_setter(
		"Contract",
		None,
		"field_order",
		frappe.as_json(field_order),
		"Data",
		for_doctype=True,
		validate_fields_for_doctype=False,
	)
	frappe.clear_cache(doctype="Contract")


def set_contract_list_view_fields():
	"""Keep Contract list view focused for Legal users."""
	visible_fields = {
		"company",
		"workflow_state",
		"sf_contract_lifecycle_status",
		"sf_contract_type",
	}
	hidden_fields = {
		"party_name",
		"status",
		"sf_contractor",
		"sf_contract_health_score",
		"fulfilment_status",
		"signed_on",
		"is_signed",
		"sf_signed_contract_document",
		"sf_compliance_tracker",
	}

	for fieldname in visible_fields:
		make_property_setter("Contract", fieldname, "in_list_view", "1", "Check")

	for fieldname in hidden_fields:
		make_property_setter("Contract", fieldname, "in_list_view", "0", "Check")

	if frappe.db.exists("DocField", {"parent": "Contract", "fieldname": "workflow_state"}):
		make_property_setter("Contract", "workflow_state", "label", "Workflow State", "Data")

	frappe.clear_cache(doctype="Contract")


def clear_contract_custom_field_descriptions():
	"""Remove helper text below app-added Contract fields for a cleaner legal form."""
	fieldnames = (
		"sf_signed_contract_document",
		"submitted_for_signing",
		"company",
		"sf_contract_lifecycle_status",
		"sf_contractor",
		"sf_contract_type",
		"sf_subsidiary_signee",
		"sf_contract_health_score",
		"sf_contract_health_reason",
		"sf_compliance_tracker",
	)

	for fieldname in fieldnames:
		frappe.db.set_value(
			"Custom Field",
			{"dt": "Contract", "fieldname": fieldname},
			"description",
			"",
			update_modified=False,
		)

	frappe.clear_cache(doctype="Contract")


def setup_contract_customizations():
	add_signed_contract_document_field()
	add_contract_lifecycle_fields()
	add_contract_business_fields()
	add_contract_health_fields()
	add_contract_compliance_link_field()
	protect_contract_custom_fields()
	set_requires_fulfilment_always_enabled()
	sync_contract_field_order()
	set_contract_list_view_fields()
	clear_contract_custom_field_descriptions()
