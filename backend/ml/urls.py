from django.urls import path
from .views import TrainModelView, ForecastView, AutoTrainForecastView, OctoberForecastView

urlpatterns = [
    path('train/', TrainModelView.as_view(), name='train-model'),
    path('forecast/', ForecastView.as_view(), name='forecast'),
    path('auto-train/', AutoTrainForecastView.as_view(), name='auto-train'),
    path('october-forecast/', OctoberForecastView.as_view(), name='october-forecast'),
]
