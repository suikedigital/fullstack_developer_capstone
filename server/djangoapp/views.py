from datetime import datetime
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate
from .models import CarMake, CarModel
from .restapis import get_request, analyze_review_sentiments, post_review


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.
def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)
    if (count == 0):
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append(
            {
                "CarModel": car_model.name,
                "CarMake": car_model.car_make.name
            }
        )
    return JsonResponse({"CarModels": cars})


# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    data = {"userName": ""}
    return JsonResponse(data)


def get_dealerships(request, state="All"):
    if (state == "All"):
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/"+state
    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})


def get_dealer_reviews(request, dealer_id):
    if (dealer_id):
        endpoint = "/fetchReviews/dealer/" + str(dealer_id)
        reviews = get_request(endpoint)
        for review_details in reviews:
            response = analyze_review_sentiments(review_details['review'])
            review_details['sentiment'] = response['sentiment']
        return JsonResponse({"status": 200, "reviews": reviews})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


def get_dealer_details(request, dealer_id):
    if (dealer_id):
        endpoint = "/fetchDealer/"+str(dealer_id)
        dealership = get_request(endpoint)
        return JsonResponse({"status": 200, "dealer": dealership})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


# Create a `add_review` view to submit a review
@csrf_exempt
def add_review(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("Received review data:", data)

            review = {
                "time": datetime.utcnow().isoformat(),
                "name": data.get("name", "Anonymous"),
                "dealership": int(data["dealership"]),
                "review": data["review"],
                "purchase": data.get("purchase", False),
                "purchase_date": data.get("purchase_date", ""),
                "car_make": data.get("car_make", ""),
                "car_model": data.get("car_model", ""),
                "car_year": data.get("car_year", ""),
            }

            response = post_review({"review": review})
            return JsonResponse(
                {
                    "status": 200,
                    "message": "Review submitted successfully",
                    "response": response
                }
            )

        except KeyError as e:
            logger.error(f"Missing key in review submission: {e}")
            return JsonResponse(
                {
                    "status": 400,
                    "error": f"Missing field: {e}"
                }
            )

        except Exception as e:
            logger.error(f"Error in submitting review: {e}")
            return JsonResponse(
                {
                    "status": 500,
                    "error": "Internal Server Error"
                }
            )

    else:
        return JsonResponse({"status": 405, "message": "Method not allowed"})
