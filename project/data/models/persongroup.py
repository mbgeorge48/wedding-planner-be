from django.db import models


class PersonGroup(models.Model):
    person = models.ForeignKey(
        "data.Person", on_delete=models.CASCADE, related_name="group_memberships"
    )
    group = models.ForeignKey(
        "data.Group", on_delete=models.CASCADE, related_name="membership_details"
    )
    relationship_type = models.CharField(
        max_length=50, blank=True
    )
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ("person", "group")

    def __str__(self):
        return f"{self.person.first_name} in {self.group}"

