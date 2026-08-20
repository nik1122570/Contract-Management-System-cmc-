import frappe
from frappe.utils import nowdate


SAMPLE_CONTRACT_NAME = "SAMPLE - BARRICK BULYANHULU COMPLIANCE"
SAMPLE_PARTY = "BARRICK GOLD MINE LIMITED - BULYANHULU"
SAMPLE_CONTRACTOR = "Barrick Gold Mine Limited - Bulyanhulu"
SAMPLE_CONTRACT_TYPE = "Catering and Cleaning Services"


SAMPLE_OBLIGATIONS = [
	{
		"terms": "Insurance",
		"contractual_obligation": (
			"Maintain valid Commercial General Liability TZS 25.8Bn, Workers Compensation TZS 258M, "
			"and Product Liability TZS 1.29Bn."
		),
		"responsible_person": "Finance Manager / Legal Officer",
		"risk": "High",
		"evidence_required": "Valid insurance policies, premium receipts, renewal dates, certificates.",
		"compliance_status": "Compliant",
	},
	{
		"terms": "KPI Performance & Penalty Exposure",
		"contractual_obligation": (
			"Minimum KPI score 90% monthly. Below threshold may attract 15% penalty on affected category. "
			"Repeated poor performance may lead to suspension or termination."
		),
		"responsible_person": "Site Manager / Operations Manager / Contract Manager",
		"risk": "High",
		"evidence_required": (
			"Signed KPI scorecards, monthly review minutes, penalty notices if any, action plan tracker, "
			"Barrick correspondence."
		),
		"compliance_status": "Non- Compliant",
	},
	{
		"terms": "Monthly Invoicing & Revenue Collection",
		"contractual_obligation": (
			"AKO must raise monthly invoices as per approved rates and actual services delivered. Delayed invoices "
			"may delay payment cycle. Ensure all deductions, credits, penalties and taxes are properly captured before submission."
		),
		"responsible_person": "Finance Manager / Site Accountant",
		"risk": "High",
		"evidence_required": (
			"Copies of invoices, supporting schedules, signed service confirmations, statement of account, "
			"aging report, proof of submission to Barrick."
		),
		"compliance_status": "Compliant",
	},
	{
		"terms": "Statutory Compliance",
		"contractual_obligation": (
			"Maintain full compliance for PAYE, SDL, NSSF, WCF, business licence, OSHA, fire, tax returns, "
			"VAT if applicable. Non-compliance can expose AKO and threaten contract continuity."
		),
		"responsible_person": "Finance Manager / HR / Legal Officer",
		"risk": "High",
		"evidence_required": (
			"Proof of payment for PAYE, SDL, NSSF and WCF, TRA returns, business licence, OSHA certificates, "
			"insurance certificates. Must be one month behind current month at minimum."
		),
		"compliance_status": "",
	},
	{
		"terms": "Price",
		"contractual_obligation": (
			"Apply approved catering, cleaning, and fixed monthly management fee rates as per contract schedule."
		),
		"responsible_person": "Finance Manager / Site Accountant",
		"risk": "High",
		"evidence_required": (
			"Approved price schedule, invoices, service confirmations, and rate verification against contract."
		),
		"compliance_status": "Compliant",
	},
]


def create_sample_contract_compliance():
	ensure_customer(SAMPLE_PARTY)
	ensure_simple_doc("Contractor", SAMPLE_CONTRACTOR, "name1")
	ensure_simple_doc("Contract Type", SAMPLE_CONTRACT_TYPE, "type")

	for obligation in SAMPLE_OBLIGATIONS:
		ensure_simple_doc("Contract Term", obligation["terms"], "term")

	contract_name = ensure_sample_contract()
	tracker_name = ensure_sample_tracker(contract_name)

	frappe.db.commit()
	return {
		"contract": contract_name,
		"tracker": tracker_name,
		"tracker_url": f"/app/contract-compliance-tracker/{tracker_name}",
	}


def ensure_customer(customer_name):
	if frappe.db.exists("Customer", customer_name):
		return customer_name

	customer = frappe.new_doc("Customer")
	customer.customer_name = customer_name
	customer.customer_type = "Company"
	customer.insert(ignore_permissions=True)
	return customer.name


def ensure_simple_doc(doctype, value, fieldname):
	if frappe.db.exists(doctype, value):
		return value

	doc = frappe.new_doc(doctype)
	doc.set(fieldname, value)
	doc.insert(ignore_permissions=True)
	return doc.name


def ensure_sample_contract():
	existing = frappe.db.get_value("Contract", {"contract_title": SAMPLE_CONTRACT_NAME}, "name")
	if existing:
		return existing

	contract = frappe.new_doc("Contract")
	contract.contract_title = SAMPLE_CONTRACT_NAME
	contract.party_type = "Customer"
	contract.party_name = SAMPLE_PARTY
	contract.party_full_name = SAMPLE_PARTY
	contract.sf_contract_type = SAMPLE_CONTRACT_TYPE
	contract.start_date = "2026-01-01"
	contract.end_date = "2026-12-31"
	contract.contract_terms = (
		"Sample contract compliance checklist loaded from the Barrick Bulyanhulu compliance template."
	)
	contract.requires_fulfilment = 1
	contract.insert(ignore_permissions=True)
	return contract.name


def ensure_sample_tracker(contract_name):
	tracker_name = frappe.db.get_value("Contract Compliance Tracker", {"contract": contract_name}, "name")

	if tracker_name:
		tracker = frappe.get_doc("Contract Compliance Tracker", tracker_name)
		tracker.set("table_ewpx", [])
	else:
		tracker = frappe.new_doc("Contract Compliance Tracker")
		tracker.contract = contract_name

	tracker.evaluation_date = nowdate()
	tracker.party_name = SAMPLE_PARTY
	tracker.contract_type = SAMPLE_CONTRACT_TYPE

	for obligation in SAMPLE_OBLIGATIONS:
		tracker.append("table_ewpx", obligation)

	if tracker.is_new():
		tracker.insert(ignore_permissions=True)
	else:
		tracker.save(ignore_permissions=True)

	frappe.db.set_value(
		"Contract",
		contract_name,
		"sf_compliance_tracker",
		tracker.name,
		update_modified=False,
	)
	return tracker.name
