from scapy.all import ARP, Ether
from unittest.mock import MagicMock
from django.test import TestCase
import network_scanner.views


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
