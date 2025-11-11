from project.data import models


def create_person(
    *,
    firstname: str,
    lastname: str,
    email: str,
    type: models.Person.Type,
    update_existing: bool = False,
    **extra_fields
):

    if type not in models.Person.Type.values:
        type = models.Person.Type.STANDARD

    person, created = models.Person.objects.get_or_create(
        firstname=firstname.title(),
        lastname=lastname.title(),
        email=email,
        type=type,
        defaults=extra_fields,
    )

    if not created and update_existing:
        person.type = type
        person.firstname = firstname
        person.lastname = lastname
        person.email = email

        # Update any other provided extra fields
        for key, value in extra_fields.items():
            setattr(person, key, value)

        person.save()

    return person, created
