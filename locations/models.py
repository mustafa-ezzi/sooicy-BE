from django.db import models

class Location(models.Model):
    name = models.CharField(max_length=200)
    area = models.CharField(max_length=200)
    delivery_time = models.PositiveIntegerField(help_text="Delivery time in minutes")
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.area}"
