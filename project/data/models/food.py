import uuid

from django.db import models


class Food(models.Model):
    class Category(models.TextChoices):
        NONE = "NONE", "None"
        VEGETARIAN = "VEGETARIAN", "Vegetarian"
        VEGAN = "VEGAN", "Vegan"
        PESCATARIAN = "PESCATARIAN", "Pescatarian"
        GLUTEN_FREE = "GLUTEN_FREE", "Gluten-Free"
        DAIRY_FREE = "DAIRY_FREE", "Dairy-Free"
        NUT_FREE = "NUT_FREE", "Nut-Free"
        OTHER = "OTHER", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True)

    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        null=False,
        blank=True,
    )
    detail = models.CharField(max_length=255)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.category} {self.detail}"
