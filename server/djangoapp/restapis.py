import requests
import json
# import related models here
from requests.auth import HTTPBasicAuth
from .models import DealerReview  


# Create a `get_request` to make HTTP GET requests
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
        try:
        # Check if an API key is provided for authentication
        if api_key:
            # Call get method of requests library with URL, parameters, and authentication
            response = requests.get(
                url,
                headers={'Content-Type': 'application/json'},
                params=kwargs,
                auth=HTTPBasicAuth('apikey', api_key)
            )
        else:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx and 5xx)
    except requests.exceptions.HTTPError as errh:
        print ("HTTP Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print ("Oops, Something went wrong:", err)
    
    status_code = response.status_code
    print("With status {} ".format(status_code))
    
    try:
        json_data = json.loads(response.text)
    except json.JSONDecodeError as json_err:
        print("JSON Decode Error:", json_err)
        json_data = None
    
    return json_data                               auth=HTTPBasicAuth('apikey', api_key))


# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)


# Create a get_dealers_from_cf method to get dealers from a cloud function
def get_dealers_from_cf(url, **kwargs):
    # Call the get_request method to get the dealerships
    dealerships = get_request(url, **kwargs)

    # Parse the JSON result into a list of CarDealer objects
    parsed_dealerships = []
    for dealer_data in dealerships:
        parsed_dealer = CarDealer(
            address=dealer_data.get('address'),
            city=dealer_data.get('city'),
            full_name=dealer_data.get('full_name'),
            id=dealer_data.get('id'),
            lat=dealer_data.get('lat'),
            long=dealer_data.get('long'),
            short_name=dealer_data.get('short_name'),
            st=dealer_data.get('st'),
            zip=dealer_data.get('zip')
        )
        parsed_dealerships.append(parsed_dealer)

    return parsed_dealerships

def get_dealerships(request):
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/7f9258a7-d155-4677-819c-5b772acda097/dealership-package/get-dealership"
        
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)

        # Concatenate all dealer's short names
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])

        # Return a list of dealer short names as an HTTP response
        return HttpResponse(dealer_names)


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
def get_dealer_reviews_from_cf(url, dealer_id):
    # Call the get_request method with the dealer ID parameter
    reviews_data = get_request(url, dealerId=dealer_id)

    # Parse the JSON result into a list of DealerReview objects
    dealer_reviews = []
    for review_data in reviews_data:
        dealer_review = DealerReview(
            dealership=review_data.get('dealership'),
            name=review_data.get('name'),
            purchase=review_data.get('purchase'),
            review=review_data.get('review'),
            purchase_date=review_data.get('purchase_date'),
            car_make=review_data.get('car_make'),
            car_model=review_data.get('car_model'),
            car_year=review_data.get('car_year'),
            id=review_data.get('id')
        )
        
        # Determine sentiment for each review
        dealer_review.determine_sentiment(dealer_review.review)

        dealer_reviews.append(dealer_review)

    return dealer_reviews

def get_dealer_by_id_from_cf(url, dealer_id):
    # Call the get_request method with the dealer ID parameter
    return get_request(url, dealerId=dealer_id)
def get_dealers_by_state_from_cf(url, state):
    # Call the get_request method with the state parameter
    return get_request(url, state=state)
# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(dealer_review, api_key, version="2021-08-01"):
    # Define the URL for the Watson NLU service
    url = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/your_instance_id/v1/analyze"

    # Set up parameters for the NLU service
    params = {
        "version": version,
        "features": "sentiment",
        "return_analyzed_text": True,
        "text": dealer_review.review  # Assuming review text is stored in the 'review' attribute
    }

    try:
        # Make a call to the updated get_request method with authentication
        response = get_request(url, api_key=api_key, params=params, headers={'Content-Type': 'application/json'})

        # Check if the response contains sentiment information
        if 'sentiment' in response:
            # Update the sentiment attribute in the DealerReview object
            dealer_review.sentiment = response['sentiment']['document']['label']

            # Save the updated DealerReview object to the database
            dealer_review.save()

        return dealer_review.sentiment  # Return the determined sentiment label
    except Exception as e:
        print("Error analyzing sentiments:", e)
        return None
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative



