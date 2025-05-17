from rest_framework.generics import RetrieveAPIView
from project.data import models


class HomeInfoView(RetrieveAPIView):
    queryset = models.Wedding.objects.get()

    def get_queryset(self):
        return super().get_queryset()
