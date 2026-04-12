from random import randint

from project.data import models


def generate_code(person_id: str):
    def generate_code():
        return f"{person.firstname[0]}{person.lastname[0]}-{str(randint(0, 999999)).zfill(6)}"

    person = models.Person.objects.get(id=person_id)
    code = generate_code()
    while models.Person.objects.filter(invite_code=code).exists():
        code = generate_code()
    return code
