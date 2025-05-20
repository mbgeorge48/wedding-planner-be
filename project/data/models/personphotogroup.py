from django.db import models


class PersonPhotoGroup(models.Model):
    person = models.ForeignKey("data.Person", on_delete=models.CASCADE, default=None)
    photo_group = models.ForeignKey(
        "data.PhotoGroup", on_delete=models.CASCADE, default=None
    )

    class Meta:
        unique_together = ("person", "photo_group")
