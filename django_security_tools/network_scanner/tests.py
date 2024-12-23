from scapy.all import ARP, Ether
from unittest.mock import MagicMock
from django.test import TestCase
import network_scanner.views
from django.urls import reverse
from unittest.mock import patch
from .models import ScanLog
from .forms import NetworkScannerForm


class NetworkScannerViewsTests(TestCase):
    def setUp(self):
        # Create a MagicMock for srp
        self.mock_srp = MagicMock()
        network_scanner.views.srp = self.mock_srp

    # Test srp with a valid packet
    def test_srp_with_valid_packet(self):
        self.mock_srp.return_value = ([], None)  # Mocked return value
        packet = Ether() / ARP()
        result = network_scanner.views.srp(packet, timeout=2, verbose=False)

        self.assertEqual(result, ([], None))  # Mocked result
        self.mock_srp.assert_called_once()

    # Test srp with an empty packet
    def test_srp_with_empty_packet(self):
        self.mock_srp.side_effect = ValueError("Empty packet not allowed")  # Mock raises exception
        packet = ""  # Empty packet
        with self.assertRaises(ValueError):
            network_scanner.views.srp(packet, timeout=2, verbose=False)

        self.mock_srp.assert_called_once()  # Ensure srp was called

    # Test srp with invalid MAC
    def test_srp_with_invalid_mac(self):
        self.mock_srp.side_effect = ValueError("Invalid MAC address")  # Mock raises exception
        packet = Ether(dst="invalid_mac") / ARP()  # Invalid MAC
        with self.assertRaises(ValueError):
            network_scanner.views.srp(packet, timeout=2, verbose=False)

        self.mock_srp.assert_called_once()  # Ensure srp was called

    # Test srp handles timeout
    def test_srp_handles_timeout(self):
        self.mock_srp.return_value = ([], None)  # Mocked return value
        packet = Ether() / ARP()
        result = network_scanner.views.srp(packet, timeout=0.01, verbose=False)

        self.assertEqual(result, ([], None))  # Mocked result
        self.mock_srp.assert_called_once_with(packet, timeout=0.01, verbose=False)

    # Test srp with multiple packets
    def test_srp_with_multiple_packets(self):
        self.mock_srp.return_value = ([], None)  # Mocked return value
        packets = [Ether() / ARP() for _ in range(3)]
        for packet in packets:
            result = network_scanner.views.srp(packet, timeout=2, verbose=False)
            self.assertEqual(result, ([], None))  # Mocked result

        self.assertEqual(self.mock_srp.call_count, len(packets))  # Ensure srp was called for each packet
        


class NetworkScannerTests(TestCase):

    def setUp(self):
        """
        Set up initial test data and configurations.
        """
        # Create ScanLog objects for testing the scan history
        ScanLog.objects.create(ip_range="192.168.0.0/24", results='[{"ip": "192.168.0.1", "mac": "00:11:22:33:44:55"}]')
        ScanLog.objects.create(ip_range="10.0.0.0/24", results='[{"ip": "10.0.0.1", "mac": "66:77:88:99:AA:BB"}]')

    def test_index_view_get(self):
        """
        Test accessing the index view with a GET request.
        """
        response = self.client.get(reverse('network_scanner:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'network_scanner/index.html')
        self.assertIsInstance(response.context['form'], NetworkScannerForm)
        self.assertIsNone(response.context['results'])
        self.assertIsNone(response.context['error'])

    @patch('network_scanner.views.scan_network')
    def test_index_view_post_valid_ip(self, mock_scan_network):
        """
        Test submitting a valid IP range to the index view.
        """
        mock_scan_network.return_value = [{'ip': '192.168.0.1', 'mac': '00:11:22:33:44:55'}]

        response = self.client.post(reverse('network_scanner:index'), {
            'ip_range': '192.168.0.0/24',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'network_scanner/index.html')
        self.assertEqual(response.context['results'], [{'ip': '192.168.0.1', 'mac': '00:11:22:33:44:55'}])
        self.assertIsNone(response.context['error'])

    def test_index_view_post_invalid_ip(self):
        """
        Test submitting an invalid IP range to the index view.
        """
        response = self.client.post(reverse('network_scanner:index'), {
            'ip_range': 'invalid_ip_range',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'network_scanner/index.html')
        self.assertIsNone(response.context['results'])
        self.assertEqual(response.context['error'], 'Invalid form submission')

    def test_scan_history_view(self):
        """
        Test the scan history view for displaying logs.
        """
        response = self.client.get(reverse('network_scanner:scan_history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'network_scanner/scan_history.html')

        logs = response.context['logs']
        self.assertEqual(len(logs), 2)
        self.assertEqual(logs[0].ip_range, '192.168.0.0/24')
        self.assertEqual(logs[1].ip_range, '10.0.0.0/24')

    @patch('network_scanner.views.srp')
    def test_scan_network_function(self, mock_srp):
        """
        Test the `scan_network` function with mocked ARP responses.
        """
        mock_response = [
            (None, type('MockReceived', (object,), {'psrc': '192.168.0.1', 'hwsrc': '00:11:22:33:44:55'})()),
            (None, type('MockReceived', (object,), {'psrc': '192.168.0.2', 'hwsrc': '66:77:88:99:AA:BB'})()),
        ]
        mock_srp.return_value = (mock_response, None)

        from .views import scan_network
        results = scan_network("192.168.0.0/24")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], {'ip': '192.168.0.1', 'mac': '00:11:22:33:44:55'})
        self.assertEqual(results[1], {'ip': '192.168.0.2', 'mac': '66:77:88:99:AA:BB'})
        
        
