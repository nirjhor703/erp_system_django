from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import UserInfos
from django.contrib.auth.hashers import make_password, check_password

def set_module(request, module_id):
    request.session['active_module'] = module_id
    next_url = request.GET.get('next', '/')
    return redirect(next_url)


def register_view(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not full_name or not email or not password:
            messages.error(request, "All fields are required")
            return redirect("register")

        if UserInfos.objects.filter(user_email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("register")

        # Always create SU user
        last_su_user = UserInfos.objects.filter(user_id__startswith="SU").order_by('-id').first()
        last_num = int(last_su_user.user_id[2:]) if last_su_user else 0
        new_user_id = f"SU{last_num + 1:010d}"  # 12 digits: SU + 10 digits

        try:
            hashed_password = make_password(password)  # hash the password

            new_user = UserInfos.objects.create(
                user_id=new_user_id,
                login_user_id=None,
                title=None,
                user_name=full_name,
                user_email=email,
                user_phone=None,
                gender=None,
                loc_id=None,
                user_role=1,  # Superadmin role id
                tran_user_type=None,
                dob=None,
                nationality=None,
                religion=None,
                nid=None,
                passport=None,
                driving_lisence=None,
                address=None,
                corporate_id=None,
                password=hashed_password,  # store hashed password
                image=None,
                store=None,
                company_id=None,
                status=1,
                added_at=timezone.now(),
                updated_at=None
            )
            new_user.save()
            messages.success(request, f"Registration successful! User ID: {new_user_id}")
            return redirect("login")
        except Exception as e:
            messages.error(request, f"Registration failed: {str(e)}")
            return redirect("register")

    return render(request, "auth/register.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user_obj = UserInfos.objects.get(user_email=email)
        except UserInfos.DoesNotExist:
            messages.error(request, "Invalid email or password")
            return redirect("login")

        if check_password(password, user_obj.password):  # verify hashed password
            request.session['user_id'] = user_obj.user_id
            request.session['user_name'] = user_obj.user_name
            request.session['user_role'] = user_obj.user_role
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid email or password")
            return redirect("login")

    return render(request, "auth/login.html")



def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user_obj = UserInfos.objects.get(user_email=email)
        except UserInfos.DoesNotExist:
            messages.error(request, "Invalid email or password")
            return redirect("login")

        db_pass = user_obj.password

        # Check if password is hashed or plain
        if db_pass.startswith('pbkdf2_'):  # Django hashed password prefix
            password_valid = check_password(password, db_pass)
        else:
            password_valid = password == db_pass

            # If valid, hash it and save for future logins
            if password_valid:
                user_obj.password = make_password(password)
                user_obj.save()

        if password_valid:
            request.session['user_id'] = user_obj.user_id
            request.session['user_name'] = user_obj.user_name
            request.session['user_role'] = user_obj.user_role
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid email or password")
            return redirect("login")

    return render(request, "auth/login.html")



def dashboard(request):
    # check session manually
    if not request.session.get('user_id'):
        return redirect('login')

    return render(request, 'dashboard/dashboard.html')


def logout_view(request):
    request.session.flush()  # clear all session data
    return redirect('login')



