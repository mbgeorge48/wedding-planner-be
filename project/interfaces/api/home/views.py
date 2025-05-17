from rest_framework.views import APIView
from project.data import models
from rest_framework.response import Response


class HomeInfoView(APIView):
    def get(self, request, *args, **kwargs):
        wedding = models.Wedding.objects.get()

        wedding_data = {
            "id": wedding.id,
            "bride": wedding.bride.firstname,
            "groom": wedding.groom.firstname,
            "date": wedding.date,
        }

        return Response(wedding_data)
