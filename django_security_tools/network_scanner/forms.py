# network_scanner/forms.py
from django import forms

class NetworkScannerForm(forms.Form):
    ip_range = forms.CharField(label='IP Range', max_length=255, required=True)
