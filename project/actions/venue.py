from project.data import models


def create_venue(
    *,
    type=models.Venue.Type.CEREMONY,
    name: str,
    address_line1: str,
    city: str,
    postcode: str,
    description: str | None = None,
):
    venue, created = models.Venue.objects.get_or_create(
        type=type,
        name=name,
        description=description,
        address_line1=address_line1,
        city=city,
        postcode=postcode,
    )

    return venue, created


def create_hotel(
    *,
    name: str,
    address_line1: str,
    city: str,
    postcode: str,
    address_line2: str = "",
    county: str = "",
    phone_number: str = "",
    website: str = "",
):
    hotel, created = models.Venue.objects.get_or_create(
        type=models.Venue.Type.HOTEL,
        name=name,
        address_line1=address_line1,
        address_line2=address_line2,
        city=city,
        county=county,
        postcode=postcode,
        phone_number=phone_number,
        website=website,
    )

    return hotel, created
