
from django.urls import path
from . import views as education
app_name = "education"
urlpatterns = [
  path('view/',education.view,name="view"),
  path('store/',education.store,name="create"),
  path('settings/',education.settings,name="settings"),
  path("",education.create,name="register"),
  path('bulk-action/', education.bulk_action, name='bulk_action'),
  path("receipt/<uuid:id>/",education.receipt,name="receipt"),
]

