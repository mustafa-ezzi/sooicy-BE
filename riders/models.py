from django.db import models

class Rider(models.Model):
    STATUS_CHOICES = [
        ("available", "Available"),
        ("busy", "Busy"),
        ("offline", "Offline"),
    ]

    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")
    current_orders = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    total_deliveries = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.status})"
