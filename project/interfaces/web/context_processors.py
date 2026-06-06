from project.data import models


def wedding(request):
    try:
        wedding = models.Wedding.objects.first()
        if wedding and wedding.bride and wedding.groom:
            return {
                "bride": wedding.bride.firstname,
                "groom": wedding.groom.firstname,
                "date": wedding.date,
            }
    except Exception:
        pass
    return {}
