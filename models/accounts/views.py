from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
import os
import hmac
import datetime
from django.views.decorators.http import require_http_methods
from accounts.status_codes import *
from django.views.decorators.csrf import csrf_protect, csrf_exempt
# from django.contrib.auth.models import User
# from django.contrib.auth import authenticate
from django.db.models import Q
from django.utils import formats
import django.contrib.auth.hashers
from django.contrib.auth.hashers import check_password, make_password
# import django settings file
from rideshare import settings
from accounts.models import UserProfile, UserAuthenticator
from ride.models import Ride


# GET or UPDATE user
@csrf_exempt
@require_http_methods(["GET", "POST"])
def user(request, id):
    """
    GET,POST http://models:8000/api/v1/accounts/user/<user_id>/
    """
    if request.method == 'GET':
        try:
            user = UserProfile.objects.get(pk=id)
            # rides = user.Ride_set.all()
            data = {
                'rating': str(user.rating),
                'school': user.school,
                'last_name': user.last_name,
                'first_name': user.first_name,
                'email': user.email,
                'number': user.phone,
                'id': str(id),
                'status': str(HTTP_200_OK)
            }
            return JsonResponse(data, status=HTTP_200_OK)
        except UserProfile.DoesNotExist:
            data = {
                'message': 'user with id {} was not found'.format(id),
                'status': str(HTTP_404_NOT_FOUND)
            }
            return JsonResponse(data, status=HTTP_404_NOT_FOUND)
    else:
        data = json.loads(request.body.decode("utf-8"))
        try:
            user = UserProfile.objects.get(pk=id)
            if not data.get('email', "") == "":
                user.email = data['email']
            if not data.get('password', "") == "":
                user.password = make_password(data['password'])
            if not data.get('first_name', "") == "":
                user.first_name = data['first_name']
            if not data.get('last_name', "") == "":
                user.last_name = data['last_name']
            if not data.get('phone', "") == "":
                user.phone = data['phone']
            if not data.get('school', "") == "":
                user.school = data['school']
            if not data.get('rating', "") == "":
                user.rating = data['rating']
            user.save()
            data = {'status': str(HTTP_204_NO_CONTENT)}
            return JsonResponse(data, status=HTTP_204_NO_CONTENT)
        except UserProfile.DoesNotExist:
            data = {'message': 'user with id ' + id +
                    ' was not found.', 'status': str(HTTP_404_NOT_FOUND)}
            return JsonResponse(data, status=HTTP_404_NOT_FOUND)


@csrf_exempt
@require_http_methods(["POST"])
def authenticate_user(request):
    """
    POST http://models:8000/api/v1/accounts/user/authenticate/
    """
    data = json.loads(request.body.decode("utf-8"))
    email = data['email']
    user = UserProfile.objects.get(email=email)
    if check_password(data['password'], user.password):
        # handle case where user is already authenticated
        try:
            auth = UserAuthenticator.objects.get(user=user)
            # not expired
            one_day_old = datetime.datetime.now() - datetime.timedelta(days=1)
            one_day_old = one_day_old.replace(tzinfo=None)
            actual = auth.date_created
            actual = actual.replace(tzinfo=None)
            if actual > one_day_old:
                return JsonResponse(
                    {
                        'message': 'user authenticated',
                        'user_id': user.id,
                        'email': user.email,
                        'authenticator': auth.authenticator,
                        'status': str(HTTP_202_ACCEPTED)
                    },
                    status=HTTP_202_ACCEPTED
                )
            else:
                auth.delete()
        except django.core.exceptions.ObjectDoesNotExist:
            pass
        # new authenticator
        auth = UserAuthenticator(
            user=user,
            date_created=datetime.datetime.now(),
            authenticator=create_authenticator_string()
        )
        auth.save()
        return JsonResponse(
            {
                'message': 'user authenticated',
                'user_id': user.id,
                'email': user.email,
                'authenticator': auth.authenticator,
                'status': str(HTTP_202_ACCEPTED)
            },
            status=HTTP_202_ACCEPTED
        )

    return JsonResponse({"message": "User not Authenticated", "status": str(HTTP_401_UNAUTHORIZED)}, status=HTTP_401_UNAUTHORIZED)


def create_authenticator_string():
    while True:
        auth = hmac.new(
            key=settings.SECRET_KEY.encode('utf-8'),
            msg=os.urandom(32),
            digestmod='sha256').hexdigest()
        try:
            UserAuthenticator.objects.get(authenticator=auth)
        except UserAuthenticator.DoesNotExist:
            return auth


@csrf_exempt
@require_http_methods(['POST'])
def verify_authenticator(request):
    """
    POST http://models:8000/api/v1/accounts/user/authenticate/verify/
    """
    try:
        data = json.loads(request.body.decode("utf-8"))
        # exists
        auth = UserAuthenticator.objects.get(
            authenticator=data['authenticator'])
        # not expired
        one_day_old = datetime.datetime.now() - datetime.timedelta(days=1)
        one_day_old = one_day_old.replace(tzinfo=None)
        actual = auth.date_created
        actual = actual.replace(tzinfo=None)
        if actual > one_day_old:
            return JsonResponse({"message": "User Authenticated", "status": str(HTTP_202_ACCEPTED)}, status=HTTP_202_ACCEPTED)
        else:
            auth.delete()
            return JsonResponse({"message": "User not Authenticated", "status": str(HTTP_401_UNAUTHORIZED)}, status=HTTP_401_UNAUTHORIZED)
    except django.core.exceptions.ObjectDoesNotExist:
        return JsonResponse({"message": "User not Authenticated", "status": str(HTTP_401_UNAUTHORIZED)}, status=HTTP_401_UNAUTHORIZED)
    except django.core.exceptions.MultipleObjectsReturned:
        # todo: unauthenticate all UserAuthenticator models that have
        # authenticator==data['authenticator']
        return JsonResponse({"message": "User not Authenticated", "status": str(HTTP_401_UNAUTHORIZED)}, status=HTTP_401_UNAUTHORIZED)


@csrf_exempt
@require_http_methods(['POST'])
def unauthenticate(request):
    """
    POST http://models:8000/api/v1/accounts/user/unauthenticate/
    """
    data = json.loads(request.body.decode("utf-8"))
    # exists
    auth = UserAuthenticator.objects.get(
        authenticator=data['authenticator'])

    auth.delete()
    return JsonResponse({"message": "User Unauthenticated", "status": str(HTTP_200_OK)}, status=HTTP_200_OK)


@csrf_exempt
@require_http_methods(["PUT"])
def create_user(request):
    """
    PUT http://localhost:8000/api/v1/accounts/user/
    """
    data = json.loads(request.body.decode("utf-8"))
    new_user = UserProfile(
        email=data['email'],
        password=make_password(data['password']),
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone=data['phone'],
        school=data['school'],
        rating=0
    )
    new_user.save()
    dataresult = {
        'status': str(HTTP_201_CREATED),
        'user_id': str(new_user.id),
        'email': new_user.email,
        'first_name': new_user.first_name,
        'last_name': new_user.last_name,
        'phone': new_user.phone,
        'school': new_user.school,
        'rating': str(new_user.rating)
    }
    return JsonResponse(dataresult, status=HTTP_201_CREATED)


@csrf_exempt
@require_http_methods(["POST"])
def delete_user(request, id):
    """
    POST http://localhost:8000/api/v1/accounts/delete/<user_id>/
    """
    try:
        user = UserProfile.objects.get(pk=id)
        user.delete()
        data = {'status': str(HTTP_204_NO_CONTENT)}
        return JsonResponse(data, status=HTTP_204_NO_CONTENT)
    except UserProfile.DoesNotExist:
        data = {'message': 'user with id ' + id +
                ' was not found.', 'status': str(HTTP_404_NOT_FOUND)}
        return JsonResponse(data, status=HTTP_404_NOT_FOUND)


@csrf_exempt
@require_http_methods(["GET"])
def user_rides(request, id):
    """
    GET http://localhost:8000/api/v1/accounts/user/<user_id>/rides/
    """
    if request.method == 'GET':
        try:
            # user = UserProfile.objects.get(pk=id)
            # rides = Ride.objects.filter(driver=id)
            rides = Ride.objects.filter(driver=id)
            driver_rides = []
            for ride in rides:
                driver_ride = {}
                driver_ride["id"] = ride.pk
                driver_ride["driver"] = str(ride.driver)
                driver_ride["available_seats"] = str(ride.openSeats)
                driver_ride["departure"] = str(
                    "{:%b %d, %Y %H:%M}".format(ride.departure))
                driver_ride["status"] = str(ride.status)
                driver_rides.append(driver_ride)

            rides = Ride.objects.filter(passenger=id)
            passenger_rides = []
            for ride in rides:
                passenger_ride = {}
                passenger_ride["id"] = ride.pk
                passenger_ride["driver"] = str(ride.driver)
                passenger_ride["available_seats"] = str(ride.openSeats)
                passenger_ride["departure"] = str(
                    "{:%b %d, %Y}".format(ride.departure))
                passenger_ride["status"] = str(ride.status)
                passenger_rides.append(passenger_ride)
            data = {
                'driver_rides': json.dumps(driver_rides),
                'passenger_rides': json.dumps(passenger_rides),
                'status': str(HTTP_200_OK)
            }
            return JsonResponse(data, status=HTTP_200_OK)
        except UserProfile.DoesNotExist:
            data = {'message': 'user with id ' + id +
                    ' was not found.', 'status': str(HTTP_404_NOT_FOUND)}
            return JsonResponse(data, status=HTTP_404_NOT_FOUND)
