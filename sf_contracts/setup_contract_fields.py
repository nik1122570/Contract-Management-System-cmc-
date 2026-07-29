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
				"options": "Pending\nActive\nExpired\nCompleted\nTerminated",
				"default": "Pending",
				"insert_after": "status",
				"allow_on_submit": 1,
				"in_list_view": 1,
				"in_standard_filter": 1,
				"no_copy": 1,
				"description": "Legal-facing contract status used for NEST-style contract tracking.",
			},
			{
				"fieldname": "sf_completion_date",
				"label": "Completion Date",
				"fieldtype": "Date",
				"insert_after": "sf_contract_lifecycle_status",
				"allow_on_submit": 1,
				"depends_on": "eval:doc.sf_contract_lifecycle_status=='Completed'",
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
	frappe.clear_cache(doctype="Contract")


def add_contract_business_fields():
	"""Add SF Group business fields used for legal contract reporting."""
	custom_fields = {
		"Contract": [
			{
				"fieldname": "sf_contractor",
				"label": "Contractor",
				"fieldtype": "Data",
				"insert_after": "party_name",
				"allow_on_submit": 1,
				"in_list_view": 1,
				"in_standard_filter": 1,
				"description": "External contractor, supplier, customer, or counterparty name used for legal reporting.",
			},
			{
				"fieldname": "sf_contract_type",
				"label": "Contract Type",
				"fieldtype": "Data",
				"insert_after": "sf_contractor",
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
				"allow_on_submit": 1,
				"description": "Name of the SF Group or subsidiary officer who signed the contract.",
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
	add_contract_compliance_link_field()
	sync_contract_field_order()
