from django.db import models

# Create your models here.
class ScanLog(models.Model):
    ip_range = models.CharField(max_length=255)
    scanned_at = models.DateTimeField(auto_now_add=True)
    results = models.TextField()

    def __str__(self):
        return f"Scan on {self.ip_range} at {self.scanned_at}"