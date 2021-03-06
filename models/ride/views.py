from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
from django.views.decorators.http import require_http_methods
from accounts.status_codes import *
from django.views.decorators.csrf import csrf_protect, csrf_exempt

from ride.models import Ride, RideRequest, DropoffLocation
from accounts.models import UserProfile


@csrf_exempt
@require_http_methods(["GET", "POST"])
def ride(request, id):
    """
    GET,POST http://models:8000/api/v1/ride/ride/<id>/
    """
    if request.method == 'GET':
        try:
            ride = Ride.objects.get(pk=id)
            driver = UserProfile.objects.get(pk=ride.driver.pk)
            passengers = ride.passenger.all()
            dropoffLocations = ride.dropoffLocation.all()
            dropoffLocations_serialized = []
            for dropoffLocation in dropoffLocations:
                dropoffLocations_serialized.append({
                    'name': dropoffLocation.name,
                    'address': dropoffLocation.address,
                    'city': dropoffLocation.city,
                    'state': dropoffLocation.state,
                    'zipcode': dropoffLocation.zipcode,
                })
            data = {
                'ride_status': str(ride.status),
                'dropoffLocations': dropoffLocations_serialized,
                'passengers': str(passengers),
                'departure': str("{:%b %d, %Y %H:%M}".format(ride.departure)),
                'available_seats': str(ride.openSeats),
                'driver': str(driver),
                'driver_email': str(driver.email),
                'status': str(HTTP_200_OK),
                'ride_id': id,
            }
            return JsonResponse(data, status=HTTP_200_OK)
        except Ride.DoesNotExist:
            data = {
                'message': 'ride with id ' + id + ' was not found.',
                'status': str(HTTP_404_NOT_FOUND)
            }
            return JsonResponse(data, status=HTTP_404_NOT_FOUND)
    else:
        data = json.loads(request.body.decode("utf-8"))
        try:
            ride = Ride.objects.get(pk=id)
            if not data.get('driver', "") == "":
                driver = UserProfile.objects.get(pk=data['driver'])
                ride.driver = driver
            if not data.get('open_seats', "") == "":
                ride.openSeats = data['open_seats']
            if not data.get('departure', "") == "":
                ride.departure = data['departure']
            if not data.get('ride_status', "") == "":
                ride.ride_status = data['ride_status']
            ride.save()
            data = {'status': str(HTTP_204_NO_CONTENT)}
            return JsonResponse(data, status=HTTP_204_NO_CONTENT)
        except UserProfile.DoesNotExist:
            data = {'message': 'ride with id ' + id +
                    ' was not found.', 'status': str(HTTP_404_NOT_FOUND)}
            return JsonResponse(data, status=HTTP_404_NOT_FOUND)


@csrf_exempt
@require_http_methods(["PUT"])
def create_ride(request):
    """
    PUT http://models:8000/api/v1/ride/ride/
    """
    data = json.loads(request.body.decode("utf-8"))
    # driver = UserProfile.objects.get(user=request.user)
    driver = UserProfile.objects.get(pk=data['driver'])
    new_ride = Ride(
        driver=driver,
        openSeats=data['open_seats'],
        departure=data['departure'],
        status=0
    )
    new_ride.save()
    data = {
        'status': str(HTTP_201_CREATED),
        'id': str(new_ride.id),
        'open_seats': new_ride.openSeats,
        'departure': new_ride.departure
    }
    return JsonResponse(data, status=HTTP_201_CREATED)


@csrf_exempt
@require_http_methods(["POST"])
def delete_ride(request, id):
    """
    POST http://models:8000/api/v1/ride/ride/delete/<id>/
    """
    try:
        ride = Ride.objects.get(pk=id)
        ride.delete()
        data = {'status': str(HTTP_204_NO_CONTENT)}
        return JsonResponse(data, status=HTTP_204_NO_CONTENT)
    except UserProfile.DoesNotExist:
        data = {'message': 'ride with id ' + id +
                ' was not found.', 'status': str(HTTP_404_NOT_FOUND)}
        return JsonResponse(data, status=HTTP_404_NOT_FOUND)


@csrf_exempt
@require_http_methods(["GET"])
def all_rides(request):
    """
    GET http://models:8000/api/v1/ride/rides/
    """
    if request.method == 'GET':
        # user = UserProfile.objects.get(pk=id)
        # rides = Ride.objects.filter(driver=id)
        rides = Ride.objects.all()
        rides_list = []
        for ride in rides:
            driver_ride = {}
            driver_ride["id"] = ride.pk
            driver_ride["driver"] = str(ride.driver)
            driver_ride["available_seats"] = str(ride.openSeats)
            driver_ride["departure"] = str(
                "{:%b %d, %Y %H:%M}".format(ride.departure))
            driver_ride["status"] = str(ride.status)
            rides_list.append(driver_ride)
        data = {
            'rides_list': json.dumps(rides_list),
            'status': str(HTTP_200_OK)
        }
        return JsonResponse(data, status=HTTP_200_OK)

    return JsonResponse({'message':'invalid request', 'status': str(HTTP_404_NOT_FOUND)}, status=HTTP_404_NOT_FOUND)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def ride_request(request, id):
    """
    GET,POST http://models:8000/api/v1/ride/rideRequest/<id>/
    """
    try:
        riderequest = RideRequest.objects.get(pk=id)
        data = {'ride': str(riderequest.ride.id), 'passenger': str(riderequest.passenger.id), 'driver-confirm': str(
            riderequest.driverConfirm), 'ride-confirm': str(riderequest.rideConfirm), 'status': str(HTTP_200_OK)}
        return JsonResponse(data, status=HTTP_200_OK)
    except Ride.DoesNotExist:
        data = {'message': 'ride request with id ' + id +
                ' was not found.', 'status': str(HTTP_404_NOT_FOUND)}
        return JsonResponse(data, status=HTTP_404_NOT_FOUND)


@csrf_exempt
@require_http_methods(["PUT"])
def create_ride_request(request):
    """
    PUT http://models:8000/api/v1/ride/rideRequest/
    """
    data = json.loads(request.body.decode("utf-8"))
    ride = Ride.objects.get(pk=data['ride_id'])
    passenger = UserProfile.objects.get(pk=data['passenger_id'])

    new_ride_request = RideRequest.objects.create(
        ride=ride, passenger=passenger, driverConfirm=False, rideConfirm=False)
    new_ride_request.save()
    dataresult = {
        'status': str(HTTP_201_CREATED), 'id': str(new_ride_request.id)}
    return JsonResponse(dataresult, status=HTTP_201_CREATED)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def dropoff_location(request, id):
    if request.method == 'GET':
        try:
            dropoff_location = DropoffLocation.objects.get(pk=id)
            data = {'name': str(dropoff_location.name), 'address': str(dropoff_location.address), 'city': str(
                dropoff_location.city), 'state': str(dropoff_location.state), 'zipcode': str(dropoff_location.zipcode), 'status': str(HTTP_200_OK)}
            return JsonResponse(data, status=HTTP_200_OK)
        except DropoffLocation.DoesNotExist:
            data = {'message': 'Dropoff Location with id ' + id +
                    ' was not found.', 'status': str(HTTP_404_NOT_FOUND)}
            return JsonResponse(data, status=HTTP_404_NOT_FOUND)
    else:
        data = json.loads(request.body.decode("utf-8"))
        try:
            dropoff_location = DropoffLocation.objects.get(pk=id)
            if not data.get('name', "") == "":
                dropoff_location.name = data['name']
            if not data.get('address', "") == "":
                dropoff_location.address = data['address']
            if not data.get('city', "") == "":
                dropoff_location.city = data['city']
            if not data.get('state', "") == "":
                dropoff_location.state = data['state']
            if not data.get('zipcode', "") == "":
                dropoff_location.zipcode = data['zipcode']
            dropoff_location.save()
            data = {'status': str(HTTP_204_NO_CONTENT)}
            return JsonResponse(data, status=HTTP_204_NO_CONTENT)
        except UserProfile.DoesNotExist:
            data = {'message': 'Dropoff Location with id ' + id +
                    ' was not found.', 'status': str(HTTP_404_NOT_FOUND)}
            return JsonResponse(data, status=HTTP_404_NOT_FOUND)


@csrf_exempt
@require_http_methods(["PUT"])
def create_dropoff_location(request):
    data = json.loads(request.body.decode("utf-8"))
    new_dropoff_location = DropoffLocation.objects.create(name=data['name'], address=data[
                                                          'address'], city=data['city'], state=data['state'], zipcode=data['zipcode'])
    new_dropoff_location.save()
    dataresult = {
        'status': str(HTTP_201_CREATED), 'id': str(new_dropoff_location.id)}
    return JsonResponse(dataresult, status=HTTP_201_CREATED)


# SERVICES list
# GET
# - driver, open seats, departure time, status
# POST
# -
