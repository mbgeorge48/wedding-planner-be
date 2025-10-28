from project.data import models
from random import randint


def generate_code(person_id: str):
    def generate_code():
        return f"{person.firstname[0]}{person.lastname[0]}-{str(randint(0, 999999)).zfill(6)}"

    person = models.Person.objects.get(id=person_id)
    existing_codes = models.Person.objects.all().values_list("invite_code", flat=True)
    code = generate_code()
    while code in existing_codes:
        code = generate_code()
    return code
