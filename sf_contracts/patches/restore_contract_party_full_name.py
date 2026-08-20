from sf_contracts.setup_contract_fields import (
	add_contract_party_compatibility_fields,
	protect_contract_custom_fields,
	sync_contract_field_order,
)


def execute():
	add_contract_party_compatibility_fields()
	protect_contract_custom_fields()
	sync_contract_field_order()
