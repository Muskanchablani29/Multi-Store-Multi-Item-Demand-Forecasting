from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ForecastViewSet, ModelEvaluationViewSet

router = DefaultRouter()
router.register(r'results', ForecastViewSet, basename='forecast')
router.register(r'evaluations', ModelEvaluationViewSet, basename='evaluation')

urlpatterns = [path('', include(router.urls))]
