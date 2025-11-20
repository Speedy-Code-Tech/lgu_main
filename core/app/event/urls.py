
from django.urls import path
from . import views
urlpatterns = [
  path('view/',views.view,name='event'),
  path('view/<int:id>',views.show,name='show_event'),
  path('edit/<int:id>',views.edit,name='edit_event'),
  path('create/',views.create,name='create_event'),
  path('destroy/',views.destroy,name='destroy_event'),
]

urlpatterns+=[
  path('calendar/', views.calendar, name='event_calendar'),     # ← NEW
    path('api/events/', views.event_api, name='event_api'),
]
