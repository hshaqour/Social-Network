from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
import json
from django.core.paginator import Paginator


from .models import User, Post


def index(request):

    posts = Post.objects.all().order_by('-timestamp')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "posts": page_obj
    })
    


def submit_post(request):
    print("submit_post view has been reached")
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"})
    
    #To confirm content
    try:
        data = json.loads(request.body)
        content = data.get("content")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"})

    if not content:
        return JsonResponse({"error": "Content required"})
    
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User is not authenticated"})
    
    #Saving each post to the Post model
    post = Post(
        poster = request.user,
        contents = content
    )
    post.save()
    return JsonResponse({"message": "Post successfuly made."})


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    followers_count = profile_user.followers.count()
    following_count = profile_user.following.count()
    is_following = request.user.is_authenticated and profile_user.followers.filter(id=request.user.id).exists()

    posts = Post.objects.filter(poster=profile_user).order_by('-timestamp')


    return render(request, "network/profile.html", {
        "profile_user": profile_user,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following,
        "posts": posts
    })


def follow(request, username):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User must be logged in."})
    
    profile_user = get_object_or_404(User, username=username)
    if request.user == profile_user:
        return JsonResponse({"error": "Cannot follow yourself."})
    
    if profile_user.followers.filter(id=request.user.id).exists():
        profile_user.followers.remove(request.user)
        action = "unfollowed"
    else:
        profile_user.followers.add(request.user)
        action = "followed"
    
    return JsonResponse({"message": f"Successfully {action} {username}."})



def check_auth(request):
    return JsonResponse({"authenticated": True})




def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
