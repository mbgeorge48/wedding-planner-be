from rest_framework.generics import RetrieveAPIView
from project.data import models


class HomeInfoView(RetrieveAPIView):
    def get():
        return None

    # queryset = models.Wedding.objects.get()

    # def get_queryset(self):
    #     return super().get_queryset()
