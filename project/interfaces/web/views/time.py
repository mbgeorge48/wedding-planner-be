from django.http import HttpResponse
from datetime import datetime


def load_time(request):
    now = datetime.now().strftime("%H:%M:%S")
    return HttpResponse(f"<p>Server time: {now}</p>")
