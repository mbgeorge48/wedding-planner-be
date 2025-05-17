import uuid

from django.db import models


class PersonFood(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True)

    person = models.ForeignKey("data.Person", on_delete=models.CASCADE)
    food = models.ForeignKey("data.Food", on_delete=models.CASCADE)

    class Meta:
        ordering = ["-created"]
        unique_together = ("person", "food")
