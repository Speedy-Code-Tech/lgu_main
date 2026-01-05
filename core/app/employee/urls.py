
from django.urls import path
from . import views
app_name = 'employee'
urlpatterns = [
  path('',views.index,name='view'),
  path('create/',views.create,name='create'),
  path('view/<int:id>',views.show,name='show'),
  path('edit/<int:id>',views.edit,name='edit'),
  path('destroy/',views.destroy,name='destroy'),
]

