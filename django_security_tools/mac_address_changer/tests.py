from django.test import TestCase
from .models import Interface
from .views import validate_mac, generate_mac, change_mac_command
from django.urls import reverse
import subprocess
from unittest.mock import patch


class MacChangerTests(TestCase):
    def setUp(self):
        """
        Set up initial test data.
        """
        # Create test interfaces
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

    def test_mac_validation(self):
        """
        Test the MAC address validation function.
        """
        valid_mac = "00:1A:2B:3C:4D:5E"
        invalid_mac = "001A2B3C4D5E"
        invalid_mac_format = "ZZ:ZZ:ZZ:ZZ:ZZ:ZZ"

        self.assertTrue(validate_mac(valid_mac))
        self.assertFalse(validate_mac(invalid_mac))
        self.assertFalse(validate_mac(invalid_mac_format))

    def test_generate_mac(self):
        """
        Test the generate MAC API endpoint.
        """
        response = self.client.get(reverse("generate_mac"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("mac_address", data)
        self.assertTrue(validate_mac(data["mac_address"]))

    @patch("subprocess.check_output")
    def test_find_interfaces(self, mock_check_output):
        """
        Test the find interfaces API endpoint.
        """
        mock_check_output.return_value = b"""
        eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        ether 00:1A:2B:3C:4D:5E  txqueuelen 1000  (Ethernet)
        wlan0: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        ether 12:34:56:78:9A:BC  txqueuelen 1000  (Ethernet)
        """

        response = self.client.get(reverse("find_interfaces"))
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("interfaces", data)
        self.assertEqual(len(data["interfaces"]), 2)

        # Check that the parsed interfaces match the mock data
        self.assertEqual(data["interfaces"][0]["name"], "eth0")
        self.assertEqual(data["interfaces"][0]["mac"], "00:1A:2B:3C:4D:5E")
        self.assertEqual(data["interfaces"][1]["name"], "wlan0")
        self.assertEqual(data["interfaces"][1]["mac"], "12:34:56:78:9A:BC")


    @patch("subprocess.run")
    def test_change_mac(self, mock_run):
        """
        Test changing the MAC address for an interface.
        """
        new_mac = "22:33:44:55:66:77"
        mock_run.return_value = None  # Simulate successful subprocess calls
        response = self.client.post(reverse("change_mac"), {
            "interface": self.interface1.name,
            "mac": new_mac,
        })
        self.assertRedirects(response, reverse("index"))

        # Reload the interface from the database and check its MAC
        self.interface1.refresh_from_db()
        self.assertEqual(self.interface1.mac_address, new_mac)

    @patch("subprocess.run")
    def test_revert_mac(self, mock_run):
        """
        Test reverting the MAC address to its original value.
        """
        new_mac = "22:33:44:55:66:77"
        mock_run.return_value = None  # Simulate successful subprocess calls

        # Change the MAC address first
        self.client.post(reverse("change_mac"), {
            "interface": self.interface1.name,
            "mac": new_mac,
        })

        # Revert the MAC address
        response = self.client.post(reverse("revert_mac"))
        self.assertRedirects(response, reverse("index"))

        # Reload the interface from the database and check its MAC
        self.interface1.refresh_from_db()
        self.assertEqual(self.interface1.mac_address, self.interface1.original_mac)
        self.assertIsNone(self.interface1.last_changed)

    @patch("subprocess.run")
    def test_invalid_mac_change(self, mock_run):
        """
        Test changing the MAC address with an invalid value.
        """
        invalid_mac = "ZZ:ZZ:ZZ:ZZ:ZZ:ZZ"
        mock_run.return_value = None  # Simulate successful subprocess calls
        response = self.client.post(reverse("change_mac"), {
            "interface": self.interface1.name,
            "mac": invalid_mac,
        })
        self.assertRedirects(response, reverse("index"))

        # Check that the MAC address did not change
        self.interface1.refresh_from_db()
        self.assertEqual(self.interface1.mac_address, self.interface1.original_mac)

    @patch("subprocess.run")
    def test_revert_no_original_mac(self, mock_run):
        """
        Test reverting the MAC address when no original MAC is set.
        """
        # Remove the original MAC from an interface
        self.interface1.original_mac = None
        self.interface1.save()

        response = self.client.post(reverse("revert_mac"))
        self.assertRedirects(response, reverse("index"))

        # Verify that the correct error message is displayed
        messages = list(response.wsgi_request._messages)
        error_messages = [str(msg) for msg in messages]
        self.assertTrue(
            any("Error: No interface found to revert." in msg for msg in error_messages),
            f"Expected error message not found. Actual messages: {error_messages}"
        )
