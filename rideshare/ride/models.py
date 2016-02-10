from django.db import models
from accounts import UserProfile

STATUS_CHOICES = (
	(0, 'open'),
	(1, 'full'),
	(2, 'departed'),
	(3, 'completed'),
)

class Ride(models.Model):
	driver = models.ForeignKey(UserProfile, models.SET_NULL, null=True)
	openSeats = models.IntegerField()
	departure = models.DateTimeField()
	status = models.IntegerField(choices=STATUS_CHOICES)

class RidePassenger(models.Model):
	passenger = models.ForeignKey(UserProfile, models.SET_NULL, null=True)
	ride = models.ForeignKey(Ride, models.SET_NULL, null=True)
	
class RideRequest(models.Model):
	passenger = models.ForeignKey(UserProfile, models.SET_NULL, null=True)
	ride = models.ForeignKey(Ride, models.SET_NULL, null=True)
	driverConfirm = models.BooleanField()
	archived = models.BooleanField()

class DropoffLocation(models.Model):
	name = models.CharField()
	address = models.CharField()
	city = models.CharField()
	state = models.CharField()
	zipcode = models.IntegerField()

class RideDropoffLocation(models.Model):
	dropoffLocation = models.ForeignKey(DropoffLocation, models.SET_NULL, null=True)
	ride = models.ForeignKey(Ride, models.SET_NULL, null=True)
	