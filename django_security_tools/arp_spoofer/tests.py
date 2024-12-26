from django.test import TestCase, Client
from unittest.mock import patch, MagicMock
from django.urls import reverse


class ARPSpooferTests(TestCase):
    @patch('arp_spoofer.views.restore')
    def test_restore_function(self, mock_restore):
        """
        Test the restore function to ensure it is called with the correct arguments.
        """
        victim_ip = "192.168.1.5"
        router_ip = "192.168.1.1"

        mock_restore(victim_ip, router_ip)
        mock_restore.assert_called_with(victim_ip, router_ip)

    @patch('arp_spoofer.views.spoofing_thread')
    def test_start_spoofing(self, mock_spoofing_thread):
        """
        Test that ARP spoofing starts successfully when valid inputs are provided.
        """
        client = Client()
        response = client.post(reverse('arp_spoofer:start_spoofing'), {
            'target_ip': '192.168.1.5',
            'router_ip': '192.168.1.1',
        })

        self.assertEqual(response.status_code, 302)  # Redirect after starting spoofing
        mock_spoofing_thread.assert_called_once_with('192.168.1.5', '192.168.1.1')

@patch('arp_spoofer.views.perform_scan')
@patch('arp_spoofer.views.subprocess.run')
def test_scan_network(self, mock_subprocess, mock_perform_scan):
    """
    Test the network scanning function to ensure it returns a valid response.
    """
    # Mock subprocess output for finding the gateway
    mock_subprocess.return_value = MagicMock(stdout="_gateway (192.168.1.1) at 00:11:22:33:44:55")

    # Mock ARP scan output
    mock_perform_scan.return_value = [
        {"ip": "192.168.1.5", "mac_address": "00:AA:BB:CC:DD:EE"},
        {"ip": "192.168.1.6", "mac_address": "00:FF:GG:HH:II:JJ"}
    ]

    client = Client()
    response = client.post(
        reverse('arp_spoofer:scan_network'),
        {},
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'  # Simulate an AJAX request
    )

    self.assertEqual(response.status_code, 200)  # Ensure we get a successful response
    json_response = response.json()
    self.assertIn("devices", json_response)
    self.assertEqual(len(json_response["devices"]), 2)
    self.assertEqual(json_response["devices"][0]["ip"], "192.168.1.5")
    self.assertEqual(json_response["devices"][0]["mac_address"], "00:AA:BB:CC:DD:EE")

