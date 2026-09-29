from django.urls import path
from .views import TrainModelView, ForecastView

urlpatterns = [
    path('train/', TrainModelView.as_view(), name='train-model'),
    path('forecast/', ForecastView.as_view(), name='forecast'),
]
