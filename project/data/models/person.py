from django.db import models


class Person(models.Model):
    class Type(models.TextChoices):
        STANDARD = "STANDARD", "Standard"
        BRIDESMAID = "BRIDESMAID", "Bridesmaid"
        GROOMSMEN = "GROOMSMEN", "Groomsmen"
        IMMEDIATEFAMILY = "IMMEDIATEFAMILY", "Immediate Family"
        BRIDEGROOM = "BRIDEGROOM", "Bride/Groom"

    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    email = models.EmailField()
