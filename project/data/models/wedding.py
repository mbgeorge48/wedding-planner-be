import uuid

from django.db import models


class Wedding(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True)

    bride = models.ForeignKey(
        "data.Person",
        on_delete=models.PROTECT,
        default=None,
        related_name="bride",
    )
    groom = models.ForeignKey(
        "data.Person",
        on_delete=models.PROTECT,
        default=None,
        related_name="groom",
    )
    ceremony_venue = models.ForeignKey(
        "data.Venue",
        on_delete=models.CASCADE,
        related_name="ceremony_wedding",
        null=True,
        blank=True,
    )
    reception_venue = models.ForeignKey(
        "data.Venue",
        on_delete=models.CASCADE,
        related_name="reception_wedding",
        null=True,
        blank=True,
    )

    date = models.DateField()
    ceremony_start_time = models.TimeField()
    reception_start_time = models.TimeField()
    evening_only_start_time = models.TimeField()
    description = models.TextField(blank=True)

    is_rsvp_open = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.pk and models.Wedding.objects.exists():
            raise Exception("Only one Wedding instance is allowed.")
        super().save(*args, **kwargs)

    def create(self, *args, **kwargs):
        if not self.pk and models.Wedding.objects.exists():
            raise Exception("Only one Wedding instance is allowed.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.groom.firstname} & {self.bride.firstname}'s Wedding"
