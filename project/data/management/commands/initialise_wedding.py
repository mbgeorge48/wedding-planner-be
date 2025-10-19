# library/management/commands/create_book.py
from django.core.management.base import BaseCommand
from project.actions.person import create_person
from project.actions.venue import create_venue
from project.data.models import Wedding, Venue


class Command(BaseCommand):
    help = "Creates a new Wedding from user input"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Let's create a new wedding!"))

        # bride
        print("=" * 8)
        print("BRIDE")
        print("=" * 8)
        firstname = input("Enter the firstname: ")
        lastname = input("Enter the lastname: ")
        email = input("Enter the email: ")
        # Code for generating invite codes
        bride, _ = create_person(
            firstname=firstname, lastname=lastname, email=email, type="BRIDEGROOM"
        )

        # groom
        print("=" * 8)
        print("GROOM")
        print("=" * 8)
        firstname = input("Enter the firstname: ")
        lastname = input("Enter the lastname: ")
        email = input("Enter the email: ")
        # Code for generating invite codes
        groom, _ = create_person(
            firstname=firstname, lastname=lastname, email=email, type="BRIDEGROOM"
        )

        def get_venue_info():
            print("=" * 8)
            print("VENUE")
            print("=" * 8)
            name = input("Enter the name: ")
            address_line1 = input("Enter the first line of the address: ")
            city = input("Enter the city: ")
            postcode = input("Enter the postcode: ")
            type_choice = input(
                "Enter the type of venue: [c for Ceremony, r for Reception] "
            )
            create_venue(
                name=name,
                address_line1=address_line1,
                city=city,
                postcode=postcode,
                type="RECEPTION" if type_choice != "c" else "CEREMONY",
            )

        get_venue_info()
        second_venue = input("Is there a 2nd venue: [y for yes, n for no]")
        if second_venue == "y":
            get_venue_info()

        print("=" * 8)
        print("WEDDING")
        print("=" * 8)
        date = input("Enter the date: ")
        start_time = input("Enter the starting time: ")

        wedding = Wedding.objects.create(
            bride=bride,
            groom=groom,
            ceremony_venue=Venue.objects.filter(type="CEREMONY").get(),
            reception_venue=Venue.objects.filter(type="RECEPTION").get(),
            date=date,
            start_time=start_time,
        )

        self.stdout.write(self.style.SUCCESS(f"✅ Created book: {wedding}"))
