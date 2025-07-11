from django.urls import path
from . import views

app_name = 'closet'

urlpatterns = [
    path('', views.clothing_items_list, name="list"),
    path('new-item/', views.clothing_item_new, name="new-item"),
    path('<int:pk>/', views.clothing_item_page, name="page"),
    path('delete/<int:pk>', views.clothing_item_delete, name="delete-item")
]