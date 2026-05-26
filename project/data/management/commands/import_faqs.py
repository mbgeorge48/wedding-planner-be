import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from project.data.models import WeddingFAQ


class Command(BaseCommand):
    help = "Populates the database with Wedding FAQs from a JSON file"

    def add_arguments(self, parser):
        # Allow passing a custom path if needed, otherwise fallback to default
        parser.add_argument(
            "--file",
            type=str,
            help="Path to the JSON file containing FAQs data",
            default=os.path.join(settings.BASE_DIR, "your_app", "data", "faqs.json"),
        )

    def handle(self, *args, **options):
        file_path = options["file"]

        if not os.path.exists(file_path):
            raise CommandError(f"JSON file not found at path: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                faqs_data = json.load(f)
        except json.JSONDecodeError as e:
            raise CommandError(f"Failed to parse JSON file: {e}")

        self.stdout.write(f"Reading FAQs from {file_path}...")

        for index, item in enumerate(faqs_data, start=1):
            if "question" not in item or "answer" not in item:
                self.stdout.write(
                    self.style.ERROR(
                        f"Skipping invalid item at index {index}: missing keys."
                    )
                )
                continue

            faq, created = WeddingFAQ.objects.update_or_create(
                question=item["question"].strip(),
                defaults={"answer": item["answer"].strip(), "order": index},
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created FAQ: {faq.question}"))
            else:
                self.stdout.write(self.style.WARNING(f"Updated FAQ: {faq.question}"))

        self.stdout.write(self.style.SUCCESS("FAQ import complete!"))
