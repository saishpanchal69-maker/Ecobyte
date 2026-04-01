import time
import random
import requests
from .models import EwasteRequest 
from .models import UserProfile
from .forms import EwasteRequestForm
from .models import EwastePhoto
from .utils import PRICE_TABLE
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from django.core.validators import validate_email

@login_required
def admin_dashboard(request):
    ewaste_requests = EwasteRequest.objects.all().order_by("-id")
    return render(request, "dashboard.html", {
        "requests": ewaste_requests,
        "is_admin": True
    })

@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully")
            return redirect("core:profile")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "change_password.html", {"form": form})

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        try:
            validate_email(email)
            if not email:
             return render(request, "register.html", {
                 "error": "Email is required"
            })
            
            if not email.endswith("@gmail.com"):
                raise ValidationError("Only Gmail allowed")

        except ValidationError:
            return render(request, "register.html", {
                "error": "Enter valid Gmail address"
            })
        
        try:
            validate_password(password1)
        except ValidationError as e:
            return render(request, "register.html", {
        "error": e.messages
    })

        if password1 != password2:
            return render(request, "register.html", {
                "error": "Passwords do not match"
            })

        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {
                "error": "Username already exists"
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        login(request, user)
        return redirect("core:dashboard")

    return render(request, "register.html")

def home(request):
    if request.user.is_authenticated:
        if request.user.userprofile.is_agent:
            return redirect("core:agent_dashboard")  # 👈 send agent away

    return render(request, "home.html")

@login_required
def create_request(request):
    if request.method == 'POST':
        form = EwasteRequestForm(request.POST, request.FILES)
        if form.is_valid():
            ewaste_request = form.save(commit=False)
            ewaste_request.user = request.user
            ewaste_request.save()

            for img in request.FILES.getlist('images'):
                EwastePhoto.objects.create(
                    request=ewaste_request,
                    image=img
                )

            return redirect("core:user_dashboard")
    else:
        form = EwasteRequestForm()

    return render(request, 'request_pickup.html', {'form': form})

@login_required
def dashboard(request):

    if request.user.userprofile.is_agent:
        return redirect("core:agent_dashboard")

    elif request.user.userprofile.is_recycler:
        return redirect("core:recycler_dashboard")

    ewaste_requests = EwasteRequest.objects.filter(
        user=request.user
    ).order_by("-id")

    return render(request, "dashboard.html", {
        "requests": ewaste_requests,
        "is_admin": False
    })

@login_required(login_url="core:login")
def request_pickup(request):
    if request.method == "POST":
        
        images = request.FILES.getlist("images")
        qty = int(request.POST.get("quantity", 1))
        item_name = request.POST.get("item_name")
        condition = request.POST.get("condition")

        if not item_name or not condition:
            messages.error(request, "All required fields must be filled")
            return redirect("core:request_pickup")  
        images = request.FILES.getlist("images")

        if len(images) < 2 or len(images) > 5:
            messages.error(request, "Upload 2–5 images only")
            return redirect("core:request_pickup")

        if qty > 50:
            qty = 50

        ewaste = EwasteRequest.objects.create(
            user=request.user,
            item_name=item_name,
            quantity=qty,
            condition=condition,
            device_details=request.POST.get("device_details"),
            status="PENDING"
        )

        for img in images:
            EwastePhoto.objects.create(
                request=ewaste,
                image=img
            )
        request.session["pickup_data"] = {
            "house_no": request.POST.get("house_no"),
            "area": request.POST.get("area"),
            "city": request.POST.get("city"),
            "state": request.POST.get("state"),
            "pincode": request.POST.get("pincode"),
            "mobile": request.POST.get("mobile"),
}
        request.session["verify_request_id"] = ewaste.id
        return redirect("core:verify")   

    return render(request, "request_pickup.html")

@login_required
def recycler_dashboard(request):
    if not request.user.userprofile.is_recycler:
        return redirect("core:dashboard")

    requests = EwasteRequest.objects.filter(status="PENDING")

    agents = User.objects.filter(userprofile__is_agent=True)

    return render(request, "recycler_dashboard.html", {
        "requests": requests,
        "agents": agents
    })

@login_required
def update_request(request, request_id):
    if not request.user.userprofile.is_recycler:
        return redirect("core:dashboard")

    ewaste = EwasteRequest.objects.get(id=request_id)

    if request.method == "POST":
        ewaste.final_amount = request.POST.get("final_amount")
        ewaste.status = "PAID"
        ewaste.save()
        return redirect("core:recycler_dashboard")

    return render(request, "update_request.html", {
        "ewaste": ewaste
    })

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)

            if user.userprofile.is_agent:
                return redirect("core:agent_dashboard")

            elif user.userprofile.is_recycler:
                return redirect("core:recycler_dashboard")

            else:
                return redirect("core:dashboard")

        return render(request, "login.html", {"error": "Invalid username or password"})

    return render(request, "login.html")


def logout_view(request):
    is_staff = request.user.is_staff
    logout(request)

    if is_staff:
        return redirect("/admin/")
    else:
        return redirect("core:home")

@login_required
def verify_request(request):
    request_id = request.session.get("verify_request_id")
    if not request_id:
        return redirect("core:request_pickup")

    ewaste = EwasteRequest.objects.get(id=request_id)
    pickup_data = request.session.get("pickup_data")

    if not pickup_data:
        return redirect("core:request_pickup")

    if request.method == "GET":
        if "otp" not in request.session:
            otp = random.randint(100000, 999999)
            request.session["otp"] = str(otp)
            request.session["otp_time"] = time.time()
            print("OTP:", otp)

        return render(request, "verify.html", {
            "ewaste": ewaste,
            "data": pickup_data
        })

    if request.method == "POST":

        pickup_data = {
            "house_no": request.POST.get("house_no"),
            "area": request.POST.get("area"),
            "city": request.POST.get("city"),
            "state": request.POST.get("state"),
            "pincode": request.POST.get("pincode"),
            "mobile": request.POST.get("mobile"),
        }
        request.session["pickup_data"] = pickup_data

        entered_otp = request.POST.get("otp", "").strip()
        session_otp = request.session.get("otp", "")
        otp_time = request.session.get("otp_time", 0)

        if time.time() - otp_time > 120:
            request.session.pop("otp", None)
            return render(request, "verify.html", {
                "ewaste": ewaste,
                "data": pickup_data,
                "error": "OTP expired. Please resend OTP."
            })

        if entered_otp != session_otp:
            return render(request, "verify.html", {
                "ewaste": ewaste,
                "data": pickup_data,
                "error": "Invalid OTP"
            })

        ewaste.address = (
            f"{pickup_data.get('house_no', '')}, "
            f"{pickup_data.get('area', '')}, "
            f"{pickup_data.get('city', '')}, "
            f"{pickup_data.get('state', '')} - "
            f"{pickup_data.get('pincode', '')}"
        )
        ewaste.mobile = pickup_data.get("mobile", "")
        ewaste.save()

        for key in ["verify_request_id", "otp", "otp_time", "otp_resend_time", "pickup_data"]:
            request.session.pop(key, None)

        return render(request, "success.html")
    
@login_required
def resend_otp(request):
    last_resend = request.session.get("otp_resend_time", 0)
    current_time = time.time()

    if current_time - last_resend < 300:
        remaining = int(300 - (current_time - last_resend))
        messages.error(
            request,
            f"Wait {remaining} seconds before resending OTP."
        )
        return redirect("core:verify")

    otp = random.randint(100000, 999999)
    request.session["otp"] = str(otp)
    request.session["otp_time"] = time.time()
    request.session["otp_resend_time"] = time.time()

    print("RESENT OTP:", otp)
    messages.success(request, "OTP resent successfully.")
    return redirect("core:verify")

@login_required
def request_success(request):
    return render(request, "success.html")  

def price_list(request):
    return render(request, "price_list.html", {
        "price_table": EwasteRequest.get_price_table()
    })

@login_required
def profile_view(request):

    user = request.user

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if username:
            user.username = username

        if email:
            user.email = email

        if password:
            user.password = make_password(password)

        user.save()

        messages.success(request,"Profile updated successfully")
        return redirect("core:profile")

    return render(request,"profile.html")
@login_required
def agent_dashboard(request):

    if not request.user.userprofile.is_agent:
        return redirect("core:dashboard")

    requests = EwasteRequest.objects.filter(
        assigned_agent=request.user
    )

    return render(request, "agent_dashboard.html", {
        "requests": requests
    })

@login_required
def agent_update_status(request, request_id):

    # Allow only agents
    if not request.user.userprofile.is_agent:
        return redirect("core:dashboard")

    ewaste = get_object_or_404(
        EwasteRequest,
        id=request_id,
        assigned_agent=request.user
    )

    if ewaste.status == "VERIFIED":
        ewaste.status = "SCHEDULED"

    elif ewaste.status == "SCHEDULED":
        ewaste.status = "PICKED"

    elif ewaste.status == "PICKED":
        ewaste.status = "PAID"

    ewaste.save()

    return redirect("core:agent_dashboard")

@login_required
def assign_agent(request, request_id):
    if not request.user.userprofile.is_recycler:
        return redirect("core:dashboard")

    ewaste = get_object_or_404(EwasteRequest, id=request_id)

    agent_id = request.POST.get("agent_id")
    agent = get_object_or_404(User, id=agent_id)

    ewaste.assigned_agent = agent
    ewaste.status = "SCHEDULED"
    ewaste.save()

    return redirect("core:recycler_dashboard")