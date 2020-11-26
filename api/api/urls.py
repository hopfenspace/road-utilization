from django.contrib import admin
from django.urls import path

from road_utilization import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/put', views.PutView.as_view()),
    path('api/import', views.ImportRoads.as_view()),
    path('api/getRoadUtilization', views.GetRoadUtilization.as_view()),
    path('api/getRoads', views.GetRoads.as_view())
]
