from . models import ShopCart, Category, Slide
from django.shortcuts import render


def cartread(request):
    cart = ShopCart.objects.filter(user__username=request.user.username, paid_order=False)


    cartreader = 0
    for item in cart:
        cartreader += item.quantity

    context = {
        'cartreader':cartreader
    }

    return context


def dropdown(request):
    categories = Category.objects.all()

    context = {
        'categories':categories
    }
    return context

def banner(request):
    slide =  Slide.objects.get(pk=1)
    slide2 = Slide.objects.get(pk=2)
    slide3 = Slide.objects.get(pk=3) 

    context = {
        'slide' :slide,
        'slide2':slide2,
        'slide3':slide3
    }

    return context
