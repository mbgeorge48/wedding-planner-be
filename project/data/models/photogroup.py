import uuid

from django.db import models


class PhotoGroup(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True)

    name = models.CharField(
        max_length=50,
        blank=False,
        null=False,
    )
    detail = models.CharField(max_length=255, blank=True, null=False)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.name}"
