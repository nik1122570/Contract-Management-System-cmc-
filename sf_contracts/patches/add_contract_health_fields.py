from sf_contracts.contract_lifecycle import update_lifecycle_status_for_contracts
from sf_contracts.setup_contract_fields import add_contract_health_fields, sync_contract_field_order


def execute():
	add_contract_health_fields()
	sync_contract_field_order()
	update_lifecycle_status_for_contracts()
