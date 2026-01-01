from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from core.models import LoginUsers
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password
from django.conf import settings
import os

# ==============================
# SUPER ADMIN CRUD
# ==============================

SUPER_ADMIN_ROLE_ID = 1  # Adjust based on your Roles table

def super_admin_list(request):
    super_admins = LoginUsers.objects.filter(user_role_id=SUPER_ADMIN_ROLE_ID).order_by('id')
    return render(request, 'users/super_admin_list.html', {
        'super_admins': super_admins
    })


@csrf_exempt
def create_super_admin(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        logo_file = request.FILES.get("logo")
        logo_name = None
        logo_url = None

        if logo_file:
            fs = FileSystemStorage(location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL)
            logo_name = fs.save(logo_file.name, logo_file)
            logo_url = fs.url(logo_name)  # <-- this gives proper URL

        if not name or not email or not phone or not password or not confirm_password:
            return JsonResponse({"success": False, "message": "All required fields are mandatory"})

        if password != confirm_password:
            return JsonResponse({"success": False, "message": "Passwords do not match"})

        last = LoginUsers.objects.filter(user_role_id=SUPER_ADMIN_ROLE_ID).order_by('id').last()
        if last and last.user_id.startswith("SA"):
            last_num = int(last.user_id[2:])
            next_id = f"SA{last_num + 1:09d}"
        else:
            next_id = "SA000000001"

        sa = LoginUsers.objects.create(
            user_id=next_id,
            user_name=name,
            user_email=email,
            user_phone=phone,
            password=make_password(password),
            image=logo_name,  # store file name in DB
            user_role_id=SUPER_ADMIN_ROLE_ID,
            status=1
        )

        return JsonResponse({
            "success": True,
            "id": sa.id,
            "user_id": sa.user_id,
            "name": sa.user_name,
            "email": sa.user_email,
            "phone": sa.user_phone,
            "logo_url": logo_url  # <-- send full URL to frontend
        })


@csrf_exempt
def update_super_admin(request, pk):
    if request.method == "POST":
        sa = get_object_or_404(LoginUsers, pk=pk, user_role_id=SUPER_ADMIN_ROLE_ID)
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        logo_file = request.FILES.get("logo")

        logo_url = sa.image.url if sa.image else None

        if logo_file:
            fs = FileSystemStorage(location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL)
            logo_name = fs.save(logo_file.name, logo_file)
            logo_url = fs.url(logo_name)
            sa.image = logo_name

        if not name or not email or not phone:
            return JsonResponse({"success": False, "message": "Name, Email and Phone are required"})

        if password and password != confirm_password:
            return JsonResponse({"success": False, "message": "Passwords do not match"})

        sa.user_name = name
        sa.user_email = email
        sa.user_phone = phone
        if password:
            sa.password = make_password(password)
        sa.save()

        return JsonResponse({
            "success": True,
            "id": sa.id,
            "user_id": sa.user_id,
            "name": sa.user_name,
            "email": sa.user_email,
            "phone": sa.user_phone,
            "logo_url": logo_url
        })



@csrf_exempt
def delete_super_admin(request, pk):
    if request.method == "POST":
        sa = get_object_or_404(LoginUsers, pk=pk, user_role_id=SUPER_ADMIN_ROLE_ID)
        sa.delete()
        return JsonResponse({"success": True})
