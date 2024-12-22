from django.test import TestCase, Client
from django.urls import reverse
from network_scanner.models import ScanLog
from network_scanner.forms import NetworkScannerForm
from network_scanner.scanner import scan_network
import json

class NetworkScannerTests(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.scan_url = reverse('network_scanner')
        self.history_url = reverse('scan_history')

    # 1. Test the network scanning function with a valid IP range
    def test_scan_network_valid_ip_range(self):
        ip_range = "192.168.1.1/24"
        results = scan_network(ip_range)
        self.assertIsInstance(results, list)
        for device in results:
            self.assertIn('ip', device)
            self.assertIn('mac', device)

    # 2. Test the network scanning function with an invalid IP range
    def test_scan_network_invalid_ip_range(self):
        ip_range = "invalid_range"
        with self.assertRaises(Exception):  # Expecting an exception for invalid IP range
            scan_network(ip_range)

    # 3. Test the network scanner form validity
    def test_network_scanner_form_valid(self):
        form = NetworkScannerForm(data={'ip_range': '192.168.1.1/24'})
        self.assertTrue(form.is_valid())

    # 4. Test the network scanner form invalid data
    def test_network_scanner_form_invalid(self):
        form = NetworkScannerForm(data={'ip_range': ''})
        self.assertFalse(form.is_valid())

    # 5. Test the network scanner view for a successful scan
    def test_network_scanner_view_post(self):
        response = self.client.post(self.scan_url, {'ip_range': '192.168.1.1/24'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'network_scanner/network_scanner.html')
        self.assertIn('results', response.context)

    # 6. Test the scan history view
    def test_scan_history_view(self):
        # Create a sample scan log
        ScanLog.objects.create(ip_range="192.168.1.1/24", results=json.dumps([{'ip': '192.168.1.2', 'mac': '00:11:22:33:44:55'}]))
        response = self.client.get(self.history_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'network_scanner/scan_history.html')
        self.assertContains(response, "192.168.1.1/24")

    # 7. Test the scan log model
    def test_scan_log_model(self):
        scan_log = ScanLog.objects.create(
            ip_range="192.168.1.1/24",
            results=json.dumps([{'ip': '192.168.1.2', 'mac': '00:11:22:33:44:55'}])
        )
        self.assertEqual(scan_log.ip_range, "192.168.1.1/24")
        self.assertIsInstance(scan_log.results, str)
