from sf_contracts.contract_lifecycle import update_lifecycle_status_for_contracts
from sf_contracts.setup_contract_fields import (
	add_contract_lifecycle_fields,
	migrate_contract_lifecycle_status_values,
)


def execute():
	add_contract_lifecycle_fields()
	migrate_contract_lifecycle_status_values()
	update_lifecycle_status_for_contracts()
