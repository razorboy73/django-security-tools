from django.db import models
from django.utils.timezone import now

class MacAddressHistory(models.Model):
    mac_address = models.CharField(max_length=17, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.mac_address} at {self.timestamp}"

class Interface(models.Model):
    name = models.CharField(max_length=50, unique=True)  # Interface name
    original_mac = models.CharField(max_length=17, blank=True, null=True)  # Original MAC address
    mac_address = models.CharField(max_length=17, blank=True, null=True)  # Current MAC address
    last_changed = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.name


