import uuid

from django.db import models


class Venue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    address_line1 = models.CharField("Address Line 1", max_length=255)
    address_line2 = models.CharField("Address Line 2", max_length=255, blank=True)
    city = models.CharField(max_length=100)
    county = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="UK", blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
