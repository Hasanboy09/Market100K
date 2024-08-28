from django.contrib.auth.views import LogoutView
from django.urls import path

from apps.views import HomeView, ProductListView, ProductDetailView, MarketListView, CustomLoginView, DashboardView, \
    CallCenter, PaymentView, ProfileFormView, StreamListView, StreamFormView, StreamDeleteView, StreamStatisticsListView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', HomeView.as_view(), name='home'),
    path('product-list/', ProductListView.as_view(), name='product-list'),
    path('product-detail/<str:slug>/', ProductDetailView.as_view(), name='product-detail'),
]

urlpatterns += [
    path('call-center/', CallCenter.as_view(), name='call-center'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('payment/', PaymentView.as_view(), name='payment'),
    path('profile/', ProfileFormView.as_view(), name='profile'),
]

urlpatterns += [
    path('market-list/', MarketListView.as_view(), name='market-list'),
    path('stream-form/', StreamFormView.as_view(), name='stream-form'),
    path('stream-list/', StreamListView.as_view(), name='stream-list'),
    path('stream-delete/<int:pk>', StreamDeleteView.as_view(), name='stream-delete'),
    path('stream/statistics/', StreamStatisticsListView.as_view(), name='stream-statistic'),

]
