from django.shortcuts import render
from django.db.models import Q, Count
from django.http import HttpResponse
from store.models import Product ,OrderItem, Order, Customer, Collection



def say_hello(request):
    collection = Collection()
    collection.title = 'kooft'

    return render(request,'hello.html',{ 'name': 'poria', })


