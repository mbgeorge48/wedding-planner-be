import uuid

from django.db import models


class ReceptionTable(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True)

    table_number = models.PositiveIntegerField(blank=False, null=False)
    max_guests = models.PositiveIntegerField(default=8)

    class Meta:
        ordering = ["table_number", "id"]

    def __str__(self):
        return f"Table {self.table_number}"
