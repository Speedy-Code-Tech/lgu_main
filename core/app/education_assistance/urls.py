
from django.urls import path
from . import views as education
app_name = "education"
urlpatterns = [
  path('',education.view,name="view")
]

