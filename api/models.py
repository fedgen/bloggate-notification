from django.db import models

# Create your models here.
class Log(models.Model):
    time = models.DateTimeField(null=True)
    email_type = models.CharField(max_length=20)
    destination = models.EmailField(max_length=100)
    status = models.CharField(max_length=20)
    info = models.TextField(default="")

class UserData(models.Model):
    auth_user_id = models.CharField(max_length=200, unique=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    num_read = models.PositiveSmallIntegerField(default=0)
    user_email = models.EmailField(max_length=200)

class Message(models.Model):
    user = models.ForeignKey(UserData, on_delete=models.CASCADE, related_name="messages")
    message = models.TextField()
    url = models.URLField(null=True)
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)