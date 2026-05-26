from django.db import models


class WeddingFAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField(
        help_text="Markdown or plain text format for the FAQ answer."
    )
    order = models.PositiveIntegerField(
        default=0, help_text="Used to control the display order."
    )

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Wedding FAQ"
        verbose_name_plural = "Wedding FAQs"

    def __str__(self):
        return self.question
