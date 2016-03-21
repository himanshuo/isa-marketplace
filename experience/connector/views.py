from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect, csrf_exempt
import requests
from connector.status_codes import *


@csrf_exempt
@require_http_methods(["GET"])
def home():
    return JsonResponse({}, status=HTTP_200_OK)


@csrf_exempt
@require_http_methods(["POST"])
def authenticate_user(request):
    """
    POST http://experience:8000/authenticate_user/
    """
    data = json.loads(request.body.decode("utf-8"))
    url = 'http://models:8000/api/v1/accounts/user/authenticate/'
    resp = requests.post(
        url,
        json={
            'email': data['email'],
            'password': data['password']
        }
    )
    if resp.status_code == HTTP_202_ACCEPTED:
        data = resp.json()
        return JsonResponse(
            {
                'message': 'User Authenticated',
                'authenticator': data['authenticator'],
                'user_id': data['user_id'],
                'email': data['email'],
            },
            status=HTTP_202_ACCEPTED
        )
    else:
        return JsonResponse({'message': 'Invalid Login' + str(resp.content)}, status=HTTP_401_UNAUTHORIZED)


def user_logged_in(request):
    if ('HTTP_AUTHENTICATOR' not in request.META) or ('HTTP_EMAIL' not in request.META):
        raise Exception('authenticator or email not in request.meta')
        return False
    auth = request.META.get('HTTP_AUTHENTICATOR')
    email = request.META.get('HTTP_EMAIL')
    url = 'http://models:8000/api/v1/accounts/user/authenticate/verify/'
    resp = requests.post(url, json={'authenticator': auth, 'email': email})
    if resp.status_code == HTTP_202_ACCEPTED:
        return True
    else:
        raise Exception(resp.content)


@csrf_exempt
@require_http_methods(["GET"])
def get_ride(request, id):
    if not user_logged_in(request):
        return JsonResponse({'message': 'Unauthenticated User'}, status=HTTP_401_UNAUTHORIZED)
    url = "http://models:8000/" + "api/v1/ride/ride/" + id + "/"
    resp = requests.get(url)
    if resp.status_code == HTTP_200_OK:
        data = resp.json()
        return JsonResponse({'message': 'Ride found', "data": data}, status=HTTP_200_OK)
    else:
        return JsonResponse({'message': 'Ride not found'}, status=HTTP_401_UNAUTHORIZED)


@csrf_exempt
@require_http_methods(["GET"])
def user_rides(request, id):
    if not user_logged_in(request):
        return JsonResponse({'message': 'Unauthenticated User'}, status=HTTP_401_UNAUTHORIZED)
    url = "http://models:8000/" + "api/v1/accounts/user/" + id + "/rides/"
    resp = requests.get(url)
    if resp.status_code == HTTP_200_OK:
        data = resp.json()
        return JsonResponse({'message': 'Ride found', "data": data}, status=HTTP_200_OK)
    else:
        return JsonResponse({'message': 'Ride not found'}, status=HTTP_401_UNAUTHORIZED)


@csrf_exempt
@require_http_methods(["PUT"])
def create_ride(request):
    """
    PUT http://experience:8001/create_ride/
    """
    if not user_logged_in(request):
        return JsonResponse({'message': 'Unauthenticated User'}, status=HTTP_401_UNAUTHORIZED)
    data = json.loads(request.body.decode("utf-8"))
    url = "http://models:8000/" + "api/v1/ride/ride/"
    resp = requests.put(
        url, json={"driver": data['driver'], "open_seats": data['open_seats'], "departure": data['departure']})
    if resp.status_code == HTTP_201_CREATED:
        new_ride = resp.json()
        return JsonResponse({'message': 'Ride Created', 'ride_id': new_ride['id'], 'open_seats': new_ride['open_seats'], 'departure': new_ride['departure']}, status=HTTP_201_CREATED)
    else:
        return JsonResponse(resp.content)
        message = resp.text
        return JsonResponse({'message': message}, status=HTTP_401_UNAUTHORIZED)


@csrf_exempt
@require_http_methods(['GET'])
def user_detail(request, id):
    """
    GET http://experience:8000/user_detail/<user_id>/
    """
    if not user_logged_in(request):
        return JsonResponse({'message': 'Unauthenticated user'}, status=HTTP_401_UNAUTHORIZED)
    url = 'http://models:8000/api/v1/accounts/user/{}/'.format(id)
    resp = requests.get(url)
    if resp.status_code == HTTP_200_OK:
        return JsonResponse(resp.json())
    else:
        return JsonResponse({'message': 'failed to get user details'}, status=HTTP_401_UNAUTHORIZED)


@csrf_exempt
@require_http_methods(['PUT'])
def create_account(request):
    """
    PUT http://experience:8001/create_account/
    """
    data = json.loads(request.body.decode("utf-8"))
    url = "http://models:8000/" + "api/v1/accounts/user/"
    resp = requests.put(url, json={
        'email': data['email'],
        'password': data['password'],
        'first_name': data['first_name'],
        'last_name': data['last_name'],
        'phone': data['phone'],
        'school': data['school'],
    })

    if resp.status_code == HTTP_201_CREATED:
        new_user = resp.json()
        return JsonResponse({
            'message': 'Account Created',
            'user_id': new_user['user_id'],
            'email': new_user['email'],
            'first_name': new_user['first_name'],
            'last_name': new_user['last_name'],
            'phone': new_user['phone'],
            'school': new_user['school'],
        }, status=HTTP_201_CREATED)
    else:
        return JsonResponse({'message': str(resp.content)}, status=HTTP_401_UNAUTHORIZED)
