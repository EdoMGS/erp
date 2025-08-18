from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    # tu možeš dodati include za druge aplikacije
]
