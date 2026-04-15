from django.urls import path
from .views import (
    ContactListView,
    ContactDatatableView,
    ContactCreateView,
    ContactGetView,
    ContactUpdateView,
    ContactDeleteView,
)

urlpatterns = [
    path('',                 ContactListView.as_view(),      name='contact_list'),
    path('datatable/',       ContactDatatableView.as_view(), name='contact_datatable'),
    path('create/',          ContactCreateView.as_view(),    name='contact_create'),
    path('get/<int:pk>/',    ContactGetView.as_view(),       name='contact_get'),
    path('update/<int:pk>/', ContactUpdateView.as_view(),    name='contact_update'),
    path('delete/<int:pk>/', ContactDeleteView.as_view(),    name='contact_delete'),
]