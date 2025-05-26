from django.urls import path

from . import views

urlpatterns = [
    path('name/', views.NameCountryView.as_view(), name='name-country'),
    path('country/', views.CountryDetailView.as_view(), name='country-detail'),
    path('protected/', views.ProtectedView.as_view(), name='protected-view'),
]
