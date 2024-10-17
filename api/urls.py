from django.urls import path
from .views import recommend_bundles

urlpatterns = [
    path('recommend-bundles/', recommend_bundles, name='recommend_bundles'),
]