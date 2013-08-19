from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.db.models.signals import post_save
# Create your models here.

class PILOT1 (models.Model):
    dt_record = models.DateTimeField()
    data_type = models.CharField(max_length=20)
    imei = models.CharField(max_length=20)
    message = models.TextField()


class SystemSens (models.Model):
    dt_record = models.DateTimeField()
    data_type = models.CharField(max_length=20)
    imei = models.CharField(max_length=20)
    message = models.TextField()

""" User profile"""
class Profile(models.Model):
    user = models.OneToOneField(User, unique=True)
    name = models.CharField(max_length=20, blank=True)
    imei = models.CharField(max_length=20, blank=True)

def create_profile(sender, instance, created, **kwargs):  
    if created:  
       profile, created = Profile.objects.get_or_create(user=instance)

post_save.connect(create_profile, sender=User) 

#User.profile = property(lambda u: Profile.objects.get_or_create(user=u)[0])

class Client (models.Model):
    imei = models.CharField(max_length=20, primary_key=True)
    phone_num = models.CharField("hashed phone number", max_length=40, blank=True )
    phone_model = models.CharField(max_length=40, blank=True)
    last_upload = models.DateTimeField(blank=True)
    version = models.CharField(max_length=10, blank=True)

    """ update the client information """
    @staticmethod
    def update(imei, version, last_upload, model='', phone=''):
        # update corresponding Client model
        client = None
        try:
            client = Client.objects.get(imei = imei)
        except ObjectDoesNotExist:
            # create a new client
            client = Client(imei = imei)
        client.phone_num = phone
        client.phone_model = model
        client.last_upload = last_upload
        client.version = version
        client.save()

""" Each deployment has a coordinator and a list of participants phone numbers,
    which we use to identify the corresponding client objects """
class Deployment (models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    coordinator = models.ForeignKey(User)

class Participant (models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    phone = models.CharField("phone number", max_length=40, blank=True)
    phone_model = models.CharField(max_length=40, blank=True)
    deployment = models.ForeignKey('Deployment')
    

""" OBSOLATED """
class Deadline (models.Model):
    set_date = models.DateTimeField()
    deadline = models.DateTimeField()
    imei = models.CharField(max_length=20)
    level = models.IntegerField()



class comments (models.Model):
    text = models.TextField()
    imei = models.CharField(max_length=20)
    submit_date = models.DateTimeField()
    from_time = models.CharField(max_length=20)
    to_time = models.CharField(max_length=20)



