from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('menu-items', views.MenuItemView.as_view()), 
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    path('orders', views.orders),
    path('orders/<int:id>', views.single_order),  
    path('groups/manager/users', views.managers),
    path('groups/manager/users/<int:id>', views.managers),
    path('groups/delivery-crew/users', views.delivery_crews),
    path('groups/delivery-crews/users/<int:id>', views.delivery_crews),
    path('cart/menu-items', views.CartView.as_view()),
    path('api-token-auth/', obtain_auth_token),
    path('categories/',views.CategoryView.as_view())
]