from django.db import models


class PersonFood(models.Model):
    person = models.ForeignKey("data.Person", on_delete=models.CASCADE, default=None)
    food = models.ForeignKey("data.Food", on_delete=models.CASCADE, default=None)

    class Meta:
        unique_together = ("person", "food")
