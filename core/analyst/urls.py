from django.urls import path
from . import prediction

urlpatterns = [
    path('', prediction.analisis_view, name='analyst_view'),
]
