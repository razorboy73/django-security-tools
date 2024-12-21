from django.test import TestCase
from .models import MacAddressHistory, Interface
from .views import validate_mac

class MacChangerTests(TestCase):
    def test_mac_validation(self):
        valid_mac = "00:1A:2B:3C:4D:5E"
        invalid_mac = "001A2B3C4D5E"
        self.assertTrue(validate_mac(valid_mac))
        self.assertFalse(validate_mac(invalid_mac))

    def test_generate_mac(self):
        response = self.client.get("/generate/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("mac_address", response.json())
