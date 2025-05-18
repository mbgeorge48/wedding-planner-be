from django.contrib import admin
from project.data import models


for model_name in models.__all__:
    model = getattr(models, model_name)
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass  # Avoid double registration in case of reloads
