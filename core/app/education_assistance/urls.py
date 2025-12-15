
from django.urls import path
from . import views as education
app_name = "education"
urlpatterns = [
  path('view/',education.view,name="view"),
  path("",education.create,name="register"),
  path("receipt/<int:id>/",education.receipt,name="receipt"),
 
]

