from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from .models import MenuItem, Cart, Order, OrderItem, Category
from rest_framework.permissions import SAFE_METHODS, BasePermission, IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User, Group
from .serializers import MenuItemSerializer, CartSerializer, CategorySerialiser
from datetime import date
from rest_framework.throttling import UserRateThrottle



# Create your views here.
class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields=['price', 'category']
    filterset_fields = ['price', 'category']
    search_fields = ['title', 'category__title']
    permission_classes = [IsAdminUser|ReadOnly]
    throttle_classes = [UserRateThrottle]

   

class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerialiser
    permission_classes = [IsAdminUser|ReadOnly]
    throttle_classes = [UserRateThrottle]


        


class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAdminUser|ReadOnly]
    throttle_classes = [UserRateThrottle]

class CartView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    serializer_class = CartSerializer
    def delete(self, arg):
        Cart.objects.filter(user=self.request.user).delete()
        return Response({'Message': 'Items removed'})
    def get_queryset(self):    
        return Cart.objects.filter(user=self.request.user)
    


    
        

    
@api_view(['GET','POST', 'DELETE'])
@permission_classes([IsAdminUser])
@throttle_classes([UserRateThrottle])
def managers(request):
    if request.method == 'GET':
        manager = User.objects.filter(groups__name='Manager').all().values('id', 'username')
        return Response({"Managers": manager})
    else:
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            manager = Group.objects.get(name="Manager")
            if request.method == 'POST':
                manager.user_set.add(user)
                user.is_staff=True
                user.save()
            elif request.method == 'DELETE':
                manager.user_set.remove(user)
                user.is_staff=False
                user.save()
            return Response({"message": "ok"})
        return Response({"message": "error"}, status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def orders(request):
    if request.method == 'GET':
        if request.user.groups.filter(name='Manager').exists():
            all_orders = Order.objects.all()
            delivery_status = request.query_params.get('status')
            all_items = OrderItem.objects.all()
            if delivery_status:
                all_orders = all_orders.filter(status=delivery_status)
                all_items = all_items.filter(order__in=all_orders)
            return Response({'Orders': all_orders.values(), 'Order Items': all_items.values()})
        elif request.user.groups.filter(name='Delivery Crew').exists():
            all_deliveries = Order.objects.filter(delivery_crew=request.user).all()
            all_delivery_items = OrderItem.objects.filter(order__in=all_deliveries).all().values()
            return Response({'Orders': all_deliveries.values(), 'Order Items': all_delivery_items})
        else:
            user_orders = Order.objects.filter(user=request.user).all()
            user_items = OrderItem.objects.filter(order__in=user_orders).all().values()
            return Response({'Orders': user_orders.values(), 'Order Items': user_items})
    elif request.method == 'POST':
        carts = Cart.objects.filter(user=request.user).all()
        total = 0
        current_date = date.today()
        for cart in carts:
            total = cart.price + total
        order = Order.objects.create(
            user = request.user,
            total = total,
            date = current_date
        )
        for cart in carts:
            OrderItem.objects.create(
                order = order,
                menuitem = cart.menuitem,
                quantity = cart.quantity,
                unit_price = cart.unit_price,
                price = cart.price
            )
        carts.delete()
        return Response({'message': 'Order Made'})

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def single_order(request, id):
    if request.method == 'GET':
        user_orders = Order.objects.filter(user=request.user, id=id).all()
        user_items = OrderItem.objects.filter(order__in=user_orders).all()
        #if request.user.id == Order.user_id:
        return Response({'Order Items': user_items.values()})
        #else:
            #return Response(status.HTTP_403_FORBIDDEN)
    elif request.method == 'PATCH' or request.method == 'PUT':
        if request.user.groups.filter(name='Delivery Crew').exists():
            new_status = request.data['status']
            delivery_status = Order.objects.get(id=id)
            delivery_status.status = new_status
            delivery_status.save()
            return Response({'message': 'Status updated'})

        elif request.user.groups.filter(name='Manager').exists():
            new_status = request.data['status']
            new_delivery_user = request.data['delivery_crew']
            if new_status:
                delivery_status = Order.objects.get(id=id)
                delivery_status.status = new_status
                delivery_status.save()
            if new_delivery_user:
                delivery_user = Order.objects.get(id=id)
                delivery_user.delivery_crew = User.objects.get(username=new_delivery_user)
                delivery_user.save()
        return Response({'message': 'Manager updated'})
    
    elif request.method == 'DELETE':
        if request.user.groups.filter(name='Manager').exists():
            Order.objects.filter(id=id).delete()
            return Response({"message": "Order Deleted"})

            



@api_view(['GET','POST', 'DELETE'])
@permission_classes([IsAdminUser])
@throttle_classes([UserRateThrottle])
def delivery_crews(request):
    if request.method == 'GET':
        delivery_crew = User.objects.filter(groups__name='Delivery Crew').all().values('id', 'username')
        return Response({"Delivery Crew": delivery_crew})
    else:
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            delivery_crew = Group.objects.get(name="Delivery Crew")
            if request.method == 'POST':
                delivery_crew.user_set.add(user)
            elif request.method == 'DELETE':
                delivery_crew.user_set.remove(user)
            return Response({"message": "ok"})
        return Response({"message": "error"}, status.HTTP_400_BAD_REQUEST)

