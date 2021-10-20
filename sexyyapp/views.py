import uuid
import requests
import json

from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User 
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from . models import Category, Product , ShopCart , Slide, Payment 
from . forms import SignupForm
# Create your views here.


def index(request):
    featured = Product.objects.filter(featured=True, available=True)
    latest = Product.objects.filter(latest=True)
   

    context = {
        'featured':featured,
        'latest':latest,   
    }

    return render(request, 'index.html',context)


def categories(request):
    categories = Category.objects.all()

    context = {
        'categories':categories
    }
    return render(request, 'categories.html',context)


def single_category(request,id):
    category = Product.objects.filter(category_id=id)

    context = {
        'category':category
    }
    return render(request, 'category.html' ,context)


def products(request):
    products = Product.objects.all().filter(available=True)

    context = {
        'products':products
    }
    return render(request, 'products.html', context)


def single_product(request,id):
    details = Product.objects.get(pk=id)


    context ={
        'details':details
    }

    return render(request, 'details.html', context)



def loginform(request):
    if request.method == 'POST':
        username =request.POST['username']
        password =request.POST['password']
        user = authenticate(username=username,password=password)
        if user:
            login(request, user)
            messages.success(request, 'You are now logged in')
            return redirect('index')
        else:
            messages.info(request, 'Ensure username/password is correct and try again')
            return redirect('loginform')

    return render(request, 'login.html',)


def singupform(request):
    reg = SignupForm()
    if request.method == 'POST':
        reg = SignupForm(request.POST)
        if reg.is_valid():
            reg.save()
            messages.success(request, 'Successful')
            return redirect('index')
        else:
            messages.warning(request, reg.errors)
            return redirect('signupform')


    context = {
        'reg':reg
    }
            
    return render (request, 'signup.html', context)


def logoutt(request):
    logout(request)
    return redirect('loginform')



def password(request):
    update = PasswordChangeForm(request.user)
    if request.method  == 'POST':
        update = PasswordChangeForm(request.user, request.POST)
        if update.is_valid():
            user = update.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'password updated')
            return redirect('index')
        else:
            messages.error(request, update.errors)
            return redirect('password')

    context = {
        'update':update
    }
    return render(request, 'password.html', context)


def addtocart(request):
    if request.method =='POST':
        basket_num = str(uuid.uuid4())
        vol =  int(request.POST['quantity'])
        pid = request.POST['itemid']
        item = Product.objects.get(pk=pid)
        cart = ShopCart.objects.filter(user__username= request.user.username, paid_order=False)
        if cart:
            basket = ShopCart.objects.filter(user__username=request.user.username, product_id=item.id).first()
            if basket:
                basket.quantity += vol
                basket.save()
                messages.success(request, "product added")
                return redirect('products')
            else:
                newitem = ShopCart()
                newitem.user =request.user
                newitem.product =item
                newitem.basket_no = cart[0].basket_no
                newitem.quantity = vol
                newitem.paid_order = False
                newitem.save()
                messages.success(request, 'product added')
        else:
            newbasket = ShopCart()
            newbasket.user =request.user
            newbasket.product =item
            newbasket.basket_no = basket_num
            newbasket.quantity = vol
            newbasket.paid_order = False
            newbasket.save()
            messages.success(request, 'product added')

    return redirect('products')

def cart(request):
    cart = ShopCart.objects.filter(user__username=request.user.username, paid_order=False)
 
    subtotal = 0
    vat = 0
    total = 0

    for item in cart:
        subtotal +=item.product.price * item.quantity

    vat = 0.075 * subtotal

    total = subtotal + vat

    context = {
        'cart':cart,
        'subtotal':subtotal,
        'vat':vat,
        'total':total
    }
    return render(request, 'cart.html', context)

def checkout(request):
    cart = ShopCart.objects.filter(user__username=request.user.username, paid_order=False)
   
    subtotal = 0
    vat = 0
    total = 0

    for item in cart:
        subtotal +=item.product.price * item.quantity

    vat = 0.075 * subtotal

    total = subtotal + vat

    context = {
        'cart':cart,
        'total':total,
        'cartcode':cart 
    }

    return render (request, 'checkout.html', context)


def placeorder(request):
    if request.method == 'POST':
        api_key ='sk_test_0e8a6068679eadbbbd2a7ff3a68f60bcf767faba'
        curl ='https://api.paystack.co/transaction/initialize'
        cburl ='http://52.14.142.196//completed/'
        # cburl ='http://localhost:8000/completed/'
        total = float(request.POST['total']) * 100
        cart_code = request.POST['cart_code']
        pay_code = str(uuid.uuid4())
        user = User.objects.get(username = request.user.username)
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone = request.POST['phone']
        address = request.POST['address']
        city = request.POST['city']
        state = request.POST['state']

        headers = {'Authorization': f'Bearer {api_key}'}
        data = {'reference':pay_code, 'email':user.email, 'amount':int(total),'callback_url':cburl, 'order_number':cart_code}

        try:
            r = requests.post(curl, headers=headers, json=data)
        except Exception:
            messages.error(request, 'network busy, try again')
        else:
            transback = json.loads(r.text)
            rd_url = transback['data']['authorization_url']

            paid = Payment()
            paid.user = user
            paid.amount = total
            paid.basket_no = cart_code
            paid.pay_code = pay_code
            paid.paid_order =True
            paid.first_name = first_name
            paid.last_name = last_name
            paid.phone = phone
            paid.address = address
            paid.city = city
            paid.sate = state
            paid.save()

            bag = ShopCart.objects.filter(user__username=request.user.username, paid_order=False)
            for item in bag:
                item.paid_order = True
                item.save()
 
                stock = Product.objects.get(pk=item.product.id)
                stock.max -= item.quantity
                stock.save()

            return redirect(rd_url)
    return redirect('checkout')

def completed(request):
    user = User.objects.filter(username = request.user.username)

    context = {
        'user': user
    }
    return render(request, 'completed.html', context)


def deleteitem(request):
    itemid = request.POST['itemid']
    ShopCart.objects.filter(pk=itemid).delete()
    messages.success(request, 'product deleted')
    return redirect('cart')


def increase(request):
    itemval = request.POST['itemval']
    valid = request.POST['valid']
    update = ShopCart.objects.get(pk=valid)
    update.quantity = itemval
    update.save()
    messages.success(request, 'product quantity updated')
    return redirect('cart')

