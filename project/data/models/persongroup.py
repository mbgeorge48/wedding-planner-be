from django.db import models


class PersonGroup(models.Model):
    person = models.ForeignKey(
        "data.Person", on_delete=models.CASCADE, related_name="group_memberships"
    )
    related_person = models.ForeignKey(
        "data.Person", on_delete=models.CASCADE, related_name="related_to"
    )
    relationship_type = models.CharField(
        max_length=50, blank=True
    )  # e.g., 'partner', 'sibling', etc.
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ("person", "related_person")
