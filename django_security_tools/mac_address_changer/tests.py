from django.test import TestCase
from django.urls import reverse
from .models import Interface
from unittest.mock import patch
from .views import validate_mac


class MacAddressChangerTests(TestCase):
    def setUp(self):
        """
        Set up initial test data for the tests.
        """
        self.interface1 = Interface.objects.create(
            name="eth0",
            original_mac="00:1A:2B:3C:4D:5E",
            mac_address="00:1A:2B:3C:4D:5E",
        )
        self.interface2 = Interface.objects.create(
            name="wlan0",
            original_mac="12:34:56:78:9A:BC",
            mac_address="12:34:56:78:9A:BC",
        )

    def test_generate_mac(self):
        """
        Test the MAC address generation functionality.
        """
        response = self.client.get(reverse("mac_address_changer:generate_mac"))
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("mac_address", data)

        generated_mac = data["mac_address"]
        self.assertTrue(validate_mac(generated_mac), f"Invalid MAC generated: {generated_mac}")

    @patch("subprocess.run")
    def test_change_mac(self, mock_run):
        """
        Test changing the MAC address for an interface.
        """
        mock_run.return_value = None  # Simulate successful subprocess calls
        new_mac = "22:33:44:55:66:77"

        response = self.client.post(reverse("mac_address_changer:change_mac"), {
            "interface": self.interface1.name,
            "mac": new_mac,
        })
        self.assertRedirects(response, reverse("mac_address_changer:index"))

        # Verify the MAC address was updated in the database
        self.interface1.refresh_from_db()
        self.assertEqual(self.interface1.mac_address, new_mac)

    @patch("subprocess.run")
    def test_revert_mac(self, mock_run):
        """
        Test reverting the MAC address to its original value.
        """
        mock_run.return_value = None  # Simulate successful subprocess calls

        # Change the MAC address first
        new_mac = "22:33:44:55:66:77"
        self.client.post(reverse("mac_address_changer:change_mac"), {
            "interface": self.interface1.name,
            "mac": new_mac,
        })

        # Revert the MAC address
        response = self.client.post(reverse("mac_address_changer:revert_mac"))
        self.assertRedirects(response, reverse("mac_address_changer:index"))

        # Verify the MAC address reverted to the original value
        self.interface1.refresh_from_db()
        self.assertEqual(self.interface1.mac_address, self.interface1.original_mac)
        self.assertIsNone(self.interface1.last_changed)
