from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse('Hello World!<br><a href="/admin">Go to Admin Page</a>')
