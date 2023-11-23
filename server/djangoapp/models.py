from django.db import models
from django.utils.timezone import now


# Create your models here.

# <HINT> Create a Car Make model `class CarMake(models.Model)`:
# - Name
# - Description
# - Any other fields you would like to include in car make model
# - __str__ method to print a car make object


# <HINT> Create a Car Model model `class CarModel(models.Model):`:
# - Many-To-One relationship to Car Make model (One Car Make has many Car Models, using ForeignKey field)
# - Name
# - Dealer id, used to refer a dealer created in cloudant database
# - Type (CharField with a choices argument to provide limited choices such as Sedan, SUV, WAGON, etc.)
# - Year (DateField)
# - Any other fields you would like to include in car model
# - __str__ method to print a car make object


# <HINT> Create a plain Python class `CarDealer` to hold dealer data
# Plain Python class for CarDealer
class CarDealer:
    def __init__(self, address, city, full_name, id, lat, long, short_name, st, zip):
        # Dealer address
        self.address = address
        # Dealer city
        self.city = city
        # Dealer Full Name
        self.full_name = full_name
        # Dealer id
        self.id = id
        # Location lat
        self.lat = lat
        # Location long
        self.long = long
        # Dealer short name
        self.short_name = short_name
        # Dealer state
        self.st = st
        # Dealer zip
        self.zip = zip

    def __str__(self):
        return f"Dealer name: {self.full_name}, ID: {self.id}, City: {self.city}, State: {self.st}"

# <HINT> Create a plain Python class `DealerReview` to hold review data
class DealerReview(models.Model):
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
    ]

    dealership = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    purchase = models.CharField(max_length=100)
    review = models.TextField()
    purchase_date = models.DateField()
    car_make = models.CharField(max_length=50)
    car_model = models.CharField(max_length=50)
    car_year = models.PositiveIntegerField()
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES)
    id = models.AutoField(primary_key=True)

    def determine_sentiment(self, text):
         # Replace 'YOUR_API_KEY' and 'YOUR_URL' with your actual Watson NLU API key and URL
        api_key = '_q-chZYNYjOyxjNJ7rDiNQmQ10Tib1FyFbkIYp2Upvd1'
        api_url = 'https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/37d9d263-29d5-4a4c-a7b5-e788e20d91a3'

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        params = {
            'version': '2021-08-01',
            'features': 'emotion,sentiment',
            'text': text,
        }

        try:
            response = requests.post(api_url, headers=headers, auth=HTTPBasicAuth('apikey', api_key), params=params)
            response.raise_for_status()
            result = response.json()

            # Extract sentiment label from the Watson NLU response
            sentiment_label = result.get('sentiment', {}).get('document', {}).get('label', 'neutral')

            # Map Watson NLU label to the choices defined in the model
            self.sentiment = self.map_label_to_choice(sentiment_label)

        except requests.exceptions.RequestException as e:
            print(f"Error making Watson NLU request: {e}")
            # Set default sentiment in case of an error
            self.sentiment = 'neutral'

    @staticmethod
    def map_label_to_choice(label):
        # Map Watson NLU sentiment label to the choices defined in the model
        label_mapping = {
            'positive': 'positive',
            'negative': 'negative',
            'neutral': 'neutral',
        }
        return label_mapping.get(label, 'neutral')

    def save(self, *args, **kwargs):
        # Before saving the instance, determine sentiment
        self.determine_sentiment(self.review)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.dealership} - {self.name} - {self.car_make} {self.car_model} ({self.car_year})"