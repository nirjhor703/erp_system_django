from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password
from django.conf import settings

from core.models import LoginUsers
from core.models import Stores


# ==============================
# CONSTANTS
# ==============================

ADMIN_ROLE_ID = 2   # change if your Admin role ID is different


# ==============================
# ADMIN LIST
# ==============================

def admin_list(request):
    admins = LoginUsers.objects.filter(user_role_id=ADMIN_ROLE_ID).order_by('id')
    stores = Stores.objects.all().order_by('store_name')  # Fetch all stores
    return render(request, 'users/admin_list.html', {
        'admins': admins,
        'stores': stores,
    })


# ==============================
# CREATE ADMIN
# ==============================

@csrf_exempt
def create_admin(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        store_id = request.POST.get("store_id")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        image_file = request.FILES.get("image")

        # ---------- VALIDATION ----------
        if not all([name, email, phone, store_id, password, confirm_password]):
            return JsonResponse({
                "success": False,
                "message": "All fields are required"
            })

        if password != confirm_password:
            return JsonResponse({
                "success": False,
                "message": "Passwords do not match"
            })

        # ---------- AUTO ADMIN ID ----------
        last = LoginUsers.objects.filter(
            user_role_id=ADMIN_ROLE_ID
        ).order_by('id').last()

        if last and last.user_id.startswith("AD"):
            next_id = f"AD{int(last.user_id[2:]) + 1:09d}"
        else:
            next_id = "AD000000001"

        # ---------- IMAGE UPLOAD ----------
        image_name = None
        image_url = None

        if image_file:
            fs = FileSystemStorage()
            image_name = fs.save(image_file.name, image_file)
            image_url = fs.url(image_name)

        # ---------- CREATE ADMIN ----------
        admin = LoginUsers.objects.create(
            user_id=next_id,
            user_name=name,
            user_email=email,
            user_phone=phone,
            store_id=store_id,
            password=make_password(password),
            image=image_name,
            user_role_id=ADMIN_ROLE_ID,
            status=1
        )

        return JsonResponse({
            "success": True,
            "id": admin.id,
            "user_id": admin.user_id,
            "name": admin.user_name,
            "email": admin.user_email,
            "phone": admin.user_phone,
            "store_id": admin.store_id,
            "image_url": image_url,
            "status": admin.status
        })


# ==============================
# UPDATE ADMIN
# ==============================

@csrf_exempt
def update_admin(request, pk):
    if request.method == "POST":
        admin = get_object_or_404(
            LoginUsers,
            pk=pk,
            user_role_id=ADMIN_ROLE_ID
        )

        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        store_id = request.POST.get("store_id")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        image_file = request.FILES.get("image")

        # ---------- VALIDATION ----------
        if not all([name, email, phone, store_id]):
            return JsonResponse({
                "success": False,
                "message": "Name, Email, Phone and Store are required"
            })

        if password and password != confirm_password:
            return JsonResponse({
                "success": False,
                "message": "Passwords do not match"
            })

        # ---------- IMAGE UPDATE ----------
        image_url = None
        if image_file:
            fs = FileSystemStorage()
            image_name = fs.save(image_file.name, image_file)
            admin.image = image_name
            image_url = fs.url(image_name)
        elif admin.image:
            image_url = settings.MEDIA_URL + admin.image

        # ---------- UPDATE DATA ----------
        admin.user_name = name
        admin.user_email = email
        admin.user_phone = phone
        admin.store_id = store_id

        if password:
            admin.password = make_password(password)

        admin.save()

        return JsonResponse({
            "success": True,
            "name": admin.user_name,
            "email": admin.user_email,
            "phone": admin.user_phone,
            "store_id": admin.store_id,
            "image_url": image_url
        })


# ==============================
# DELETE ADMIN
# ==============================

@csrf_exempt
def delete_admin(request, pk):
    if request.method == "POST":
        admin = get_object_or_404(
            LoginUsers,
            pk=pk,
            user_role_id=ADMIN_ROLE_ID
        )
        admin.delete()

        return JsonResponse({
            "success": True
        })
