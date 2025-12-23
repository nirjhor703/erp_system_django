from datetime import timezone
from django.shortcuts import render
from django.http import JsonResponse
from .models import TransactionHeads, Stores, ItemManufacturers, LocationInfos, TransactionMainsTemps, TransactionDetailsTemps
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import F, Q
from django.db.models import Count, Case, When, IntegerField, Q
from pharmacy.utils.transaction import generate_tran_id
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction


def dictfetchall(cursor):
    """Return all rows from a cursor as a list of dicts."""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
def medicine_list(request):
    products = TransactionHeads.objects.all().defer('added_at', 'updated_at', 'expiry_date').order_by('id')
    paginator = Paginator(products, 10)  # 10 per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'pharmacy/medicine_list.html', {
        'products': page_obj
})

# def medicine_list(request):
#     transactions = TransactionMainsTemps.objects.all().order_by("-id")[:50]  # latest 50

#     products = []
#     for tran in transactions:
#         # Get all medicines for this transaction
#         medicines = TransactionHeads.objects.filter(groupe=tran.tran_type)  # <-- adjust if needed
#         products.append({
#             "tran_id": tran.tran_id,
#             "status": "Verified" if tran.status == 1 else "Non Verified",
#             "medicines": medicines,
#         })

#     return render(request, "pharmacy/medicine_list.html", {"products": products})
def medicine_add(request):
    # Add Medicine modal/page
    return render(request, 'pharmacy/add.html')


def product_search(request):
    q = request.GET.get('q', '').strip()
    offset = int(request.GET.get('offset', 0))
    limit = 5

    cursor = connection.cursor()

    # If no search text → show all
    if q == "":
        sql = """
            SELECT 
                t.id,
                t.tran_head_name AS name,
                t.cp,
                '' AS manufacturer,
                '' AS form,
                t.quantity,
                
                t.mrp
            FROM transaction__heads t
            ORDER BY t.id
            LIMIT %s OFFSET %s
        """
        params = [limit, offset]

    else:
        # Search by name startswith
        sql = """
            SELECT 
                t.id,
                t.tran_head_name AS name,
                t.cp,
                '' AS manufacturer,
                '' AS form,
                t.quantity,
                
                t.mrp
            FROM transaction__heads t
            WHERE t.tran_head_name LIKE %s
            ORDER BY t.id
            LIMIT %s OFFSET %s
        """
        params = [q + "%", limit, offset]

    cursor.execute(sql, params)
    data = dictfetchall(cursor)

    return JsonResponse({'results': data})

# store

def add_medicine(request):
    # Fetch only active stores (status=1)
    stores = Stores.objects.filter(status=1).order_by('store_name')
    return render(request, 'pharmacy/add.html', {'stores': stores})

def get_stores(request):
    stores = Stores.objects.filter(status=1).order_by('store_name')
    data = [
        {"id": s.id, "name": s.store_name}
        for s in stores
    ]
    return JsonResponse({"stores": data})

def get_suppliers(request):
    # Status 1 er manufacturer fetch
    manufacturers = ItemManufacturers.objects.filter(status=1).order_by('manufacturer_name')
    data = [{"id": m.id, "name": m.manufacturer_name} for m in manufacturers]
    return JsonResponse({"suppliers": data})

def get_divisions(request):
    # Only active locations (status=1)
    divisions = LocationInfos.objects.filter(status=1).order_by('division')
    data = [{"id": d.id, "name": d.division} for d in divisions]
    return JsonResponse({"divisions": data})


@csrf_exempt   # AJAX hole thakbe, na hole CSRF use koro
def create_transaction_temp(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"}, status=405)

    try:
        with transaction.atomic():   # 🔑 important line

            store_id = request.POST.get("store_id")
            tran_type = request.POST.get("tran_type")
            tran_method = request.POST.get("tran_method")
            location_name = request.POST.get("location")

            if not store_id:
                return JsonResponse({"success": False, "message": "Store required"}, status=400)

            store = Stores.objects.get(id=store_id)

            location = LocationInfos.objects.filter(
                division__iexact=location_name
            ).first()

            loc_id = location.id if location else None

            # TRAN ID
            tran_id = generate_tran_id("TRA")

            # 🔹 TABLE 1: transaction_mains_temps
            main_tran = TransactionMainsTemps.objects.create(
                tran_id=tran_id,
                tran_type=int(tran_type),
                tran_method=tran_method,
                store=store,
                loc_id=loc_id,
                tran_date=timezone.now(),
                status=1,
                discount=0
            )

            # 🔹 TABLE 2: transaction_details_temp
            TransactionDetailsTemps.objects.create(
            tran_id=tran_id,
            tran_type=int(tran_type),
            tran_method=tran_method,
            store=store,
            loc_id=loc_id,

            quantity_actual=0,
            quantity=0,
            quantity_issue=0,
            quantity_return=0,

            amount=0,
            tot_amount=0,
            discount=0,

            status=1,
            tran_date=timezone.now()
        )

        return JsonResponse({
            "success": True,
            "tran_id": tran_id
        })

    except Stores.DoesNotExist:
        return JsonResponse({"success": False, "message": "Invalid store"}, status=400)

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
    
# def test_tran_id_generation(request):
#         store = Stores.objects.first()  # any store for testing

#         tran_id = generate_tran_id("TRA")

#         TransactionMainsTemps.objects.create(
#             tran_id=tran_id,
#             tran_type = 1,
#             store=store,
#             loc_id=store.location_id,
#             tran_date=timezone.now(),
#             status=1,
#             discount=0
#         )

#         return JsonResponse({
#             "message": "Tran ID generated & saved successfully",
#             "tran_id": tran_id
#         })
@csrf_exempt
def verify_transaction(request, tran_id):
    if request.method == "POST":
        try:
            tran = TransactionMainsTemps.objects.get(tran_id=tran_id)
            tran.status = 2  # 2 = Verified
            tran.save()
            return JsonResponse({"success": True, "message": f"Transaction {tran_id} verified successfully"})
        except TransactionMainsTemps.DoesNotExist:
            return JsonResponse({"success": False, "message": "Transaction not found"})
    return JsonResponse({"success": False, "message": "Invalid request"})

def get_transaction(request, tran_id):
    try:
        tran = TransactionMainsTemps.objects.get(tran_id=tran_id)
        medicines = [m.tran_head_name for m in tran.medicines.all()]
        data = {
            "tran_id": tran.tran_id,
            "location": tran.store.division if tran.store else "",
            "store_id": tran.store.id if tran.store else None,
            "tran_date": tran.tran_date.strftime("%Y-%m-%d"),
            "supplier": tran.tran_user,
            "medicines": medicines,
            "quantity": tran.quantity,
            "unit": tran.unit.unit_name if tran.unit else "",
            "expiry_date": tran.expiry_date.strftime("%Y-%m-%d") if tran.expiry_date else "",
            "cp": tran.cp,
            "mrp": tran.mrp,
            "total": tran.net_amount,
        }
        return JsonResponse(data)
    except TransactionMainsTemps.DoesNotExist:
        return JsonResponse({"error": "Transaction not found"}, status=404)