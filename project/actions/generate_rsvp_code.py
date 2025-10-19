from project.data import models
from random import randint


def generate_code(person_id):
    def generate_code():
        return (
            f"{person.firstname[0]}{person.lastname[0]}-{str(randint(0, 999)).zfill(3)}"
        )

    person = models.Person.objects.get(id=person_id)
    existing_codes = models.Person.objects.all().values_list("invite_code", flat=True)
    code = generate_code()
    while code in existing_codes:
        code = generate_code()
    return code
