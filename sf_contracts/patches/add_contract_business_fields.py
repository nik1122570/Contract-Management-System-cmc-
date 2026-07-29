from sf_contracts.setup_contract_fields import (
	add_contract_business_fields,
	add_contract_compliance_link_field,
	sync_contract_field_order,
)


def execute():
	add_contract_business_fields()
	add_contract_compliance_link_field()
	sync_contract_field_order()
