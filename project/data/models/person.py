import uuid

from django.db import models


class Person(models.Model):
    class Type(models.TextChoices):
        STANDARD = "STANDARD", "Standard"
        BRIDESMAID = "BRIDESMAID", "Bridesmaid"
        GROOMSMEN = "GROOMSMEN", "Groomsmen"
        IMMEDIATEFAMILY = "IMMEDIATEFAMILY", "Immediate Family"
        BRIDEGROOM = "BRIDEGROOM", "Bride/Groom"

    id = models.UUIDField(primary_key=True, default=uuid.uuid, editable=False)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True)

    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    email = models.EmailField()

    type = models.CharField(
        max_length=50,
        choices=Type.choices,
        null=False,
        blank=True,
    )
    has_rsvp = models.BooleanField(default=False)

    class Meta:
        ordering = ["firstname"]

    def __str__(self):
        return f"{self.firstname} {self.lastname}, {self.type}"
