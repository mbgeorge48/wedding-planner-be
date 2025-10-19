from project.data import models


def create_person(
    *,
    firstname,
    lastname,
    email,
    type,
    phone=None,
    address=None,
    priority=models.Person.Priority.HIGH
):
    person, created = models.Person.objects.get_or_create(
        firstname=firstname,
        lastname=lastname,
        email=email,
        phone=phone,
        address=address,
        priority=priority,
        type=type,
    )

    return person, created
