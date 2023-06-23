from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('invoice/<int:national_id>', views.invoice),
    path('', admin.site.urls),
]
