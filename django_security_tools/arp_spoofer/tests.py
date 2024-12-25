from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from arp_spoofer.utils import get_gateway_info, scan_network, spoof_both, enable_port_forwarding, stop_spoofing

class ARPSpooferTests(TestCase):

    def setUp(self):
        self.client = Client()

    @patch('arp_spoofer.utils.get_gateway_info')
    def test_detect_gateway_success(self, mock_get_gateway_info):
        """Test detecting the gateway successfully"""
        mock_get_gateway_info.return_value = {'ip': '172.16.149.2', 'mac': '00:50:56:ed:9f:de'}
        response = self.client.post(reverse('arp_spoofer:index'), {'detect_gateway': '1'})
        self.assertContains(response, "Gateway detected: 172.16.149.2 (00:50:56:ed:9f:de)")
        self.assertEqual(response.status_code, 200)

    @patch('arp_spoofer.utils.scan_network')
def test_scan_network_success(self, mock_scan_network):
    mock_scan_network.return_value = [
        {'ip': '172.16.149.1', 'mac': 'f2:18:98:6a:f1:65'},
        {'ip': '172.16.149.2', 'mac': '00:50:56:ed:9f:de'},
        {'ip': '172.16.149.163', 'mac': '00:0c:29:3c:f6:d1'},
        {'ip': '172.16.149.254', 'mac': '00:50:56:f4:72:0e'},
    ]
    response = self.client.post(reverse('arp_spoofer:index'), {'scan_network': '1'})
    self.assertContains(response, "172.16.149.163")

    @patch('arp_spoofer.utils.start_spoofing_continuous')
    @patch('arp_spoofer.utils.get_gateway_info')
    def test_start_spoofing_success(self, mock_get_gateway_info, mock_start_spoofing):
        """Test starting spoofing"""
        mock_get_gateway_info.return_value = {'ip': '192.168.1.1', 'mac': 'aa:bb:cc:dd:ee:ff'}
        session = self.client.session
        session['scan_results'] = [{'ip': '192.168.1.2', 'mac': 'ff:ee:dd:cc:bb:aa'}]
        session.save()

        response = self.client.post(reverse('arp_spoofer:index'), {
            'start_spoofing': '1',
            'target': '192.168.1.2|ff:ee:dd:cc:bb:aa'
        })
        self.assertContains(response, "Spoofing started")
        self.assertEqual(self.client.session['spoofing_status'], True)
        self.assertEqual(response.status_code, 200)

    @patch('arp_spoofer.utils.stop_spoofing')
    def test_stop_spoofing(self, mock_stop_spoofing):
        """Test stopping spoofing"""
        session = self.client.session
        session['spoofing_status'] = True
        session.save()

        response = self.client.post(reverse('arp_spoofer:index'), {'stop_spoofing': '1'})
        self.assertContains(response, "Spoofing stopped")
        self.assertEqual(self.client.session['spoofing_status'], False)
        self.assertEqual(response.status_code, 200)

    def test_clear_scan_results_on_get(self):
        """Test that scan results are cleared on a GET request"""
        session = self.client.session
        session['scan_results'] = [{'ip': '192.168.1.2', 'mac': 'ff:ee:dd:cc:bb:aa'}]
        session.save()

        response = self.client.get(reverse('arp_spoofer:index'))
        self.assertIsNone(self.client.session.get('scan_results'))
        self.assertNotContains(response, "192.168.1.2")
        self.assertEqual(response.status_code, 200)
