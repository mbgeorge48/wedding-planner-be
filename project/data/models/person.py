import uuid

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from project.actions.generate_rsvp_code import generate_code


class Person(models.Model):
    class Type(models.TextChoices):
        STANDARD = "STANDARD", "Standard"
        BRIDESMAID = "BRIDESMAID", "Bridesmaid"
        GROOMSMEN = "GROOMSMEN", "Groomsmen"
        IMMEDIATEFAMILY = "IMMEDIATEFAMILY", "Immediate Family"
        BRIDEGROOM = "BRIDEGROOM", "Bride/Groom"

    class Priority(models.IntegerChoices):
        LOW = 3, "Low"
        MEDIUM = 2, "Medium"
        HIGH = 1, "High"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True)

    invite_code = models.CharField(max_length=10, unique=True, null=True)

    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    priority = models.IntegerField(choices=Priority, default=Priority.HIGH)
    type = models.CharField(
        max_length=50,
        choices=Type.choices,
        null=False,
        blank=True,
    )

    invited_to_ceremony = models.BooleanField(default=False)
    has_rsvp_ceremony = models.BooleanField(default=False)

    invited_to_reception = models.BooleanField(default=False)
    has_rsvp_reception = models.BooleanField(default=False)

    relationships = models.ManyToManyField(
        "self",
        through="data.PersonGroup",
        symmetrical=False,
        related_name="related_people",
    )

    has_plus_one = models.BooleanField(default=False)
    plus_one_name = models.CharField(max_length=255, blank=True)

    children = models.IntegerField(default=0)
    pets = models.IntegerField(default=0)

    dietary_requirements = models.ManyToManyField(
        "data.Food", through="data.PersonFood", related_name="person"
    )
    photo_groups = models.ManyToManyField(
        "data.PhotoGroup", through="data.PersonPhotoGroup", related_name="person"
    )

    class Meta:
        ordering = ["firstname"]

    def __str__(self):
        return f"{self.firstname} {self.lastname}, {self.get_type_display()}"


@receiver(post_save, sender=Person)
def assign_invite_code(sender, instance, created, **kwargs):
    if created and not instance.invite_code:
        instance.invite_code = generate_code(instance.id)
        instance.save()
