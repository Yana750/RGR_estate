from django.urls import path

from .views import RentListView, RentDetailView, RentByCategoryListView, rent_list, RentCreateView, RentUpdateView, RentDeleteView

urlpatterns = [
    path('', RentListView.as_view(), name='home'),
    path('rents/', rent_list, name='rents_by_page'),
    path('rents/create/', RentCreateView.as_view(), name='rents_create'),
    path('rents/<str:slug>/update/', RentUpdateView.as_view(), name='articles_update'),
    path('rents/<str:slug>/delete/', RentDeleteView.as_view(), name='articles_delete'),
    path('rents/<str:slug>/', RentDetailView.as_view(), name='rent_detail'),
    path('category/<str:slug>/', RentByCategoryListView.as_view(), name="rents_by_category"),
]