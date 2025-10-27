from project.data import models


def create_venue(
    *,
    type=models.Venue.Type.CEREMONY,
    name: str,
    address_line1: str,
    city: str,
    postcode: str,
    description: str = None,
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
