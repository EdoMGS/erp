from django.urls import path

from .views import worker_timer

urlpatterns = [
    path("worker-timer/", worker_timer, name="worker_timer"),
]
