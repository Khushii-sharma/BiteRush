
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Customer, Item, Restaurant, Cart, Order
import razorpay
from django.conf import settings
from django.urls import reverse

def index(request):
    return render(request, 'delivery/index.html')

def open_signup(request):
    return render(request, 'delivery/signup.html')

def open_login(request):
    return render(request, 'delivery/login.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')

    try:
        Customer.objects.get(username = username)
        return HttpResponse("Duplicate Username!")
    except:
        Customer.objects.create(
            username = username,
            password = password,
            email = email,
            mobile = mobile,
            address = address,
        )
    return render(request, 'delivery/login.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            Customer.objects.get(username=username, password=password)
            if username == 'admin':
                return render(request, 'delivery/admin_home.html')
            else:
                return redirect('customer_home', username=username)

        except Customer.DoesNotExist:
            return HttpResponse("Invalid credentials or registration failed")

    return render(request, 'delivery/login.html')

    
def open_add_restaurant(request):
    return render(request, 'delivery/add_restaurant.html')

def add_restaurant(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        picture = request.POST.get('picture')
        cuisine = request.POST.get('cuisine')
        rating = request.POST.get('rating')

    try:
        Restaurant.objects.get(name = name)
        return HttpResponse("Duplicate restaurant!")
    except:
        Restaurant.objects.create(
            name = name,
            picture = picture,
            cuisine = cuisine,
            rating = rating,
        )

    return render(request, 'delivery/admin_home.html')


def open_show_restaurant(request):
    restaurantList = Restaurant.objects.all()
    return render(request, 'delivery/show_restaurants.html', {"restaurantList": restaurantList})


def open_update_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    return render(request, 'delivery/update_restaurant.html', {"restaurant": restaurant})

def update_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        picture = request.POST.get('picture')
        cuisine = request.POST.get('cuisine')
        rating = request.POST.get('rating')

        restaurant.name = name
        restaurant.picture = picture
        restaurant.cuisine = cuisine
        restaurant.rating = rating

        restaurant.save()

    restaurantList = Restaurant.objects.all()
    return render(request, 'delivery/show_restaurants.html', {"restaurantList" : restaurantList})


def delete_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    restaurant.delete()

    restaurantList = Restaurant.objects.all();
    return render(request, 'delivery/show_restaurants.html', {"restaurantList" : restaurantList})

def open_update_menu(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    itemList = restaurant.items.all()
    return render(request, 'delivery/update_menu.html', {"itemList" : itemList, "restaurant" : restaurant})


def update_menu(request, restaurant_id):
    restaurant = Restaurant.objects.get(id=restaurant_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        vegetarian = request.POST.get('vegetarian') == 'on'
        picture = request.POST.get('picture')

        if Item.objects.filter(restaurant=restaurant, name=name).exists():
            return HttpResponse("Duplicate item for this restaurant!")

        Item.objects.create(
            restaurant=restaurant,
            name=name,
            description=description,
            price=price,
            vegetarian=vegetarian,
            picture=picture,
        )
        

    # Fetch updated items list and render page
    itemList = restaurant.items.all()
    return render(request, 'delivery/update_menu.html', {
        'restaurant': restaurant,
        'itemList': itemList
    })

def delete_item(request, item_id):
    item = Item.objects.get(id=item_id)
    restaurant_id = item.restaurant.id
    item.delete()
    return redirect('open_update_menu', restaurant_id=restaurant_id)

def edit_item(request, item_id):
    item = Item.objects.get(id=item_id)
    restaurant_id = item.restaurant.id

    if request.method == 'POST':
        item.name = request.POST.get('name')
        item.description = request.POST.get('description')
        item.price = request.POST.get('price')
        item.vegetarian = request.POST.get('vegetarian') == 'on'
        item.picture = request.POST.get('picture')
        item.save()
        return redirect('open_update_menu', restaurant_id=restaurant_id)

    return render(request, 'delivery/edit_item.html', {'item': item})

def view_menu(request, restaurant_id, username):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    itemList = restaurant.items.all()
    return render(request, 'delivery/customer_menu.html', {"itemList" : itemList, "restaurant" : restaurant, "username" : username})


def add_to_cart(request, item_id, username):
    item = get_object_or_404(Item, id=item_id)
    customer = get_object_or_404(Customer, username=username)

    cart, created = Cart.objects.get_or_create(customer=customer)
    cart.items.add(item)    
    messages.success(request, "Item added to your cart!")

    return redirect('view_menu', restaurant_id=item.restaurant.id, username=username)

def show_cart(request, username):
    customer = Customer.objects.get(username = username)
    cart = Cart.objects.filter(customer = customer).first()
    items = cart.items.all() if cart else []
    total_price = cart.total_price() if cart else 0

    return render(request, 'delivery/cart.html', {"itemList": items, "total_price": total_price, "username": username })

def checkout(request, username):
    customer = Customer.objects.get(username = username)
    cart = Cart.objects.filter(customer = customer).first()
    cart_items = cart.items.all() if cart else []
    total_price = cart.total_price() if cart else 0

    if total_price == 0:
        return render(request, 'delivery/checkout.html', {
            'username': username,
            'error': 'Your cart is empty!',
        })

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    order_data = {
        'amount': int(total_price * 100),
        'currency': 'INR',
        'payment_capture': '1',
    }
    order = client.order.create(data=order_data)

    
    return render(request, 'delivery/checkout.html', {
        'username': username,
        'cart_items': cart_items,
        'total_price': total_price,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'order_id': order['id'],
        'amount': total_price,
    })


def orders(request, username):
    customer = get_object_or_404(Customer, username=username)
    cart = Cart.objects.filter(customer=customer).first()

    cart_items = list(cart.items.all()) if cart else []
    total_price = cart.total_price() if cart else 0

    # Create the Order entry BEFORE clearing the cart items
    if cart and cart_items:
        new_order = Order.objects.create(
            customer=customer,
            total_amount=total_price,
            status="Completed"
        )
        new_order.items.set(cart_items)  # Save purchased items to the order
        cart.items.clear()              # Clear customer's active cart

    return render(request, 'delivery/orders.html', {
        'username': username,
        'customer': customer,
        'cart_items': cart_items,
        'total_price': total_price,
    })


def profile(request, username):
    customer = get_object_or_404(Customer, username=username)
    # Fetch all completed orders for this customer ordered by newest first
    user_orders = Order.objects.filter(customer=customer).order_by('-created_at')

    return render(request, 'delivery/profile.html', {
        'username': username,
        'customer': customer,
        'orders': user_orders,
    })

def customer_home(request, username):
    customer = get_object_or_404(Customer, username=username)
    restaurant_list = Restaurant.objects.all()

    return render(request, 'delivery/customer_home.html', {
        'username': username,
        'customer': customer,
        'restaurantList': restaurant_list,
    })