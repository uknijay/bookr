from django.shortcuts import render

def discover(request):
    return render(request, "main/events/discover.html")
