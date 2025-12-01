
from django.urls import path
from . import views
urlpatterns = [
    path('login/',views.index),
    path('view/',views.view_activity),
    path('done/',views.view_activity_done),
    path('update/',views.update_status),
    path('logout/',views.user_logout),
    path('add/',views.add_event),
    
]