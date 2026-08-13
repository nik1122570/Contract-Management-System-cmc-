import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter


def add_signed_contract_document_field():
	"""Add the primary signed contract attachment field to ERPNext Contract."""
	custom_fields = {
		"Contract": [
			{
				"fieldname": "sf_signed_contract_document",
				"label": "Signed Contract Document",
				"fieldtype": "Attach",
				"insert_after": "signed_on",
				"allow_on_submit": 1,
				"no_copy": 1,
				"description": "Attach the final signed contract document.",
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
				"fieldname": "sf_contract_lifecycle_status",
				"label": "Contract Lifecycle Status",
				"fieldtype": "Select",
				"options": "Draft\nActive\nExpired – Services Continuing\nClosed\nTerminated",
				"default": "Draft",
				"insert_after": "status",
				"allow_on_submit": 1,
				"in_list_view": 1,
				"in_standard_filter": 1,
				"no_copy": 1,
				"description": "Legal-facing contract lifecycle status used for contract tracking.",
			},
			{
				"fieldname": "sf_completion_date",
				"label": "Completion Date",
				"fieldtype": "Date",
				"insert_after": "sf_contract_lifecycle_status",
				"allow_on_submit": 1,
				"depends_on": "eval:doc.sf_contract_lifecycle_status=='Closed'",
				"no_copy": 1,
			},
			{
				"fieldname": "sf_termination_date",
				"label": "Termination Date",
				"fieldtype": "Date",
				"insert_after": "sf_completion_date",
				"allow_on_submit": 1,
				"depends_on": "eval:doc.sf_contract_lifecycle_status=='Terminated'",
				"no_copy": 1,
			},
			{
				"fieldname": "sf_termination_reason",
				"label": "Termination Reason",
				"fieldtype": "Small Text",
				"insert_after": "sf_termination_date",
				"allow_on_submit": 1,
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
		"Pending": "Draft",
		"Pending Execution": "Draft",
		"Executed – Awaiting Commencement": "Draft",
		"Expired": "Expired – Services Continuing",
		"Completed": "Closed",
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
	custom_fields = {
		"Contract": [
		{
			"fieldname": "sf_contractor",
			"label": "Contractor",
			"fieldtype": "Link",
			"options": "Contractor",
			"insert_after": "party_name",
			"is_system_generated": 0,
			"allow_on_submit": 1,
				"in_list_view": 1,
				"in_standard_filter": 1,
				"description": "External contractor, supplier, customer, or counterparty name used for legal reporting.",
			},
		{
			"fieldname": "sf_contract_type",
			"label": "Contract Type",
			"fieldtype": "Link",
			"options": "Contract Type",
			"insert_after": "sf_contractor",
			"is_system_generated": 0,
			"allow_on_submit": 1,
				"in_list_view": 1,
				"in_standard_filter": 1,
				"description": "Business type/category of this contract, for example supply of Energy Meters.",
			},
			{
				"fieldname": "sf_subsidiary_signee",
				"label": "Subsidiary Signee",
				"fieldtype": "Data",
				"insert_after": "signee",
				"is_system_generated": 0,
				"allow_on_submit": 1,
				"description": "Name of the SF Group or subsidiary officer who signed the contract.",
			},
		]
	}

	create_custom_fields(custom_fields, update=True)
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
				"in_list_view": 1,
				"in_standard_filter": 1,
				"no_copy": 1,
				"description": "Management traffic-light indicator calculated from signature, lifecycle, expiry, and compliance.",
			},
			{
				"fieldname": "sf_contract_health_reason",
				"label": "Contract Health Reason",
				"fieldtype": "Small Text",
				"insert_after": "sf_contract_health_score",
				"read_only": 1,
				"allow_on_submit": 1,
				"no_copy": 1,
				"description": "Main reason behind the calculated Contract Health Score.",
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
			},
			{
				"fieldname": "sf_compliance_tracker",
				"label": "Contract Compliance Tracker",
				"fieldtype": "Link",
				"options": "Contract Compliance Tracker",
				"insert_after": "sf_compliance_section",
				"read_only": 1,
				"allow_on_submit": 1,
				"no_copy": 1,
				"description": "Auto-created when Requires Fulfilment is checked.",
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

	move_after("sf_contractor", "party_name")
	move_after("sf_contract_type", "sf_contractor")
	move_after("sf_subsidiary_signee", "signee")
	move_after("sf_contract_health_score", "sf_contract_lifecycle_status")
	move_after("sf_contract_health_reason", "sf_contract_health_score")
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


def setup_contract_customizations():
	add_signed_contract_document_field()
	add_contract_lifecycle_fields()
	add_contract_business_fields()
	add_contract_health_fields()
	add_contract_compliance_link_field()
	set_requires_fulfilment_always_enabled()
	sync_contract_field_order()
