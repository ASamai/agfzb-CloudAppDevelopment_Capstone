from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
from .restapis import get_dealer_reviews_from_cf
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)
# Create a `login_request` view to handle sign in request
# View to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/login.html', context)
    else:
        return render(request, 'djangoapp/login.html', context)

# View to handle sign out request
def logout_request(request):
    # Get the user object based on session id in request
    print("Logging out `{}`...".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:index')

# View to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("/djangoapp/")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
def get_dealer_details(request, dealer_id):
    context = {}

    if request.method == "GET":
        # Define the URL for the cloud function to get dealer reviews
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/7f9258a7-d155-4677-819c-5b772acda097/dealership-package/review-get"

        # Call the get_dealer_reviews_from_cf method to get reviews for the specified dealer ID
        dealer_reviews = get_dealer_reviews_from_cf(url, dealer_id)

        # Append the list of reviews to the context
        context['dealer_reviews'] = dealer_reviews

        # Return an HTTP response, rendering the dealer details page with the list of reviews
        return render(request, 'djangoapp/dealer_details.html', context)
# ...
app_name = 'djangoapp'
urlpatterns = [
    # ... Other paths
    
    # Example path for get_dealer_details view with dealer_id as an integer parameter
    path('dealer/<int:dealer_id>/', views.get_dealer_details, name='dealer_details'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...