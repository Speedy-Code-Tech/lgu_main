
from django.urls import path
from . import views
urlpatterns = [
  path('login/',views.login,name='login'),
  path('logout/',views.user_logout,name='logout')
]

