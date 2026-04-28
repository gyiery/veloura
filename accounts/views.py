from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def user_register(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "").strip()

        if not name or not email or not password:
            messages.error(request, "Please fill all register fields.")
            return redirect("/?modal=register")

        if User.objects.filter(username=email).exists():
            messages.error(request, "This email is already registered.")
            return redirect("/?modal=register")

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name
        )

        login(request, user)
        messages.success(request, "Account created successfully.")
        return redirect("/?modal=account")

    return redirect("/")


def user_login(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "").strip()

        if not email or not password:
            messages.error(request, "Please enter email and password.")
            return redirect("/?modal=login")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful.")
            return redirect("/?modal=account")

        messages.error(request, "Invalid email or password.")
        return redirect("/?modal=login")

    return redirect("/")


def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("/")