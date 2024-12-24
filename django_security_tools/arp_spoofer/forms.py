from django import forms

class NetworkScannerForm(forms.Form):
    ip_range = forms.CharField(
        label="IP Range",
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 192.168.1.0/24'
        })
    )
