# network_scanner/views.py
from django.shortcuts import render
from .forms import NetworkScannerForm
from .scanner import scan_network
from .models import ScanLog
import json

def network_scanner_view(request):
    results = None
    if request.method == 'POST':
        form = NetworkScannerForm(request.POST)
        if form.is_valid():
            ip_range = form.cleaned_data['ip_range']
            scan_results = scan_network(ip_range)
            results = scan_results
            # Save to the database
            ScanLog.objects.create(ip_range=ip_range, results=json.dumps(scan_results))
    else:
        form = NetworkScannerForm()
    return render(request, 'network_scanner/network_scanner.html', {'form': form, 'results': results})

def scan_history_view(request):
    logs = ScanLog.objects.all()
    return render(request, 'network_scanner/scan_history.html', {'logs': logs})
