import uuid

from django.db import models


class Wedding(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid, editable=False)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True)

    bride = models.ForeignKey("data.Person", on_delete=models.PROTECT)
    groom = models.ForeignKey("data.Person", on_delete=models.PROTECT)
    venue = models.ForeignKey("data.Venue", on_delete=models.SET_NULL)

    date = models.DateField()
    start_time = models.TimeField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.bride.firstname} & {self.groom.firstname}'s Wedding at {self.venue.name}"
