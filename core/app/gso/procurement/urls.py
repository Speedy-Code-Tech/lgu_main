
from django.urls import path
from . import views
app_name = 'gso'
urlpatterns = [
  path('',views.index,name='procurement'),
  path('create/',views.create,name='procurement_create'),
  path('delete/<int:id>/',views.delete,name='procurement_delete'),
  path('view/<int:id>/',views.view,name='procurement_view'),
  path('edit/<int:id>/',views.edit,name='procurement_edit'),
]

