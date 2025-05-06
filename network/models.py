from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    #Add the followers relationship of user
    followers = models.ManyToManyField(
        'self', #A user can follow others
        symmetrical=False, #One way relationship
        related_name='following' #Allows us to access the users this user is following
    )
    pass


class Post(models.Model):
    poster = models.ForeignKey("User", on_delete=models.CASCADE, related_name="poster")
    contents = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

''' Will do as part of the last specification
class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="liked_posts")
    timestamp = models.DateTimeField(auto_now_add=True
'''