from django.test import TestCase
from .models import Interface
from .views import validate_mac, generate_mac
from django.urls import reverse
import json


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

    def test_find_interfaces(self):
        """
        Test the find interfaces API endpoint.
        """
        response = self.client.get(reverse("find_interfaces"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("interfaces", data)
        self.assertIn("instructions", data)

    def test_change_mac(self):
        """
        Test changing the MAC address for an interface.
        """
        new_mac = "22:33:44:55:66:77"
        response = self.client.post(reverse("change_mac"), {
            "interface": self.interface1.name,
            "mac": new_mac,
        })
        self.assertRedirects(response, reverse("index"))

        # Reload the interface from the database and check its MAC
        self.interface1.refresh_from_db()
        self.assertEqual(self.interface1.mac_address, new_mac)

    def test_revert_mac(self):
        """
        Test reverting the MAC address to its original value.
        """
        # Change the MAC address first
        new_mac = "22:33:44:55:66:77"
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

    def test_revert_no_last_changed(self):
        """
        Test reverting when no interface has been changed.
        """
        response = self.client.post(reverse("revert_mac"))
        self.assertRedirects(response, reverse("index"))

        # Verify that an appropriate error message is displayed
        messages = list(response.wsgi_request._messages)
        self.assertTrue(
            any("No interface found to revert." in str(msg) for msg in messages),
            "Expected error message not found."
        )   


    def test_invalid_mac_change(self):
        """
        Test changing the MAC address with an invalid value.
        """
        invalid_mac = "ZZ:ZZ:ZZ:ZZ:ZZ:ZZ"
        response = self.client.post(reverse("change_mac"), {
            "interface": self.interface1.name,
            "mac": invalid_mac,
        })
        self.assertRedirects(response, reverse("index"))

        # Check that the MAC address did not change
        self.interface1.refresh_from_db()
        self.assertEqual(self.interface1.mac_address, self.interface1.original_mac)

    def test_revert_no_original_mac(self):
        """
        Test reverting the MAC address when no original MAC is set.
        """
        # Remove the original MAC from an interface
        self.interface1.original_mac = None
        self.interface1.save()

        response = self.client.post(reverse("revert_mac"))
        self.assertRedirects(response, reverse("index"))

        # Verify that an appropriate error message is displayed
        messages = list(response.wsgi_request._messages)
        error_messages = [str(msg) for msg in messages]
        self.assertTrue(
            any("Error: No interface found to revert" in msg for msg in error_messages),
            f"Expected error message not found. Actual messages: {error_messages}"
        )
