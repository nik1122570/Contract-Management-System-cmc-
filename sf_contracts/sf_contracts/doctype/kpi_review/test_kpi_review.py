import frappe
from frappe.tests.utils import FrappeTestCase


class TestKPIReview(FrappeTestCase):
	def test_doctype_available(self):
		self.assertTrue(frappe.get_meta("KPI Review"))
