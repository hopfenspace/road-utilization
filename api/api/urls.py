from django.contrib import admin
from django.urls import path

from road_utilization import views
from frontend.views import *

urlpatterns = [
    path('', FrontendView.as_view()),
    path('admin/', admin.site.urls),
    path('api/put', views.PutView.as_view()),
    path('api/import', views.ImportRoads.as_view()),
    path('api/getRoadUtilization', views.GetRoadUtilization.as_view()),
    path('api/getRoads', views.GetRoads.as_view()),
    path('api/getSensorPositions', views.GetSensorPositions.as_view()),
    path('api/getRoadUtilizationHistory', views.GetRoadUtilizationHistory.as_view()),
    path('api/setSensorPosition', views.SetSensorPositionView.as_view())
]
