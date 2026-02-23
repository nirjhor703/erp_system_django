from datetime import timezone
import json
from math import ceil
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from pharmacy.models import *
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import F, Q
from django.db.models import Count, Case, When, IntegerField, Q

from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from itertools import chain






def dictfetchall(cursor):
    """Return all rows from a cursor as a list of dicts."""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
# def medicine_list(request):
#     products = TransactionHeads.objects.all().defer('added_at', 'updated_at', 'expiry_date').order_by('id')
#     paginator = Paginator(products, 10)  # 10 per page
#     page_number = request.GET.get('page', 1)
#     page_obj = paginator.get_page(page_number)
    
#     return render(request, 'pharmacy/medicine_list.html', {
#         'products': page_obj
# })



# def medicine_list(request):
#     # 🔹 Get filters from GET parameters
#     status_filter = request.GET.get('status', '')
#     search = request.GET.get('search', '')
#     start_date = request.GET.get('start_date', '')
#     end_date = request.GET.get('end_date', '')

#     # 🔹 Temp table: unverified
#     temp_qs = TransactionMainsTemps.objects.filter(status=1)

#     # 🔹 Main table: verified
#     main_qs = TransactionMains.objects.filter(status=2)

#     # 🔹 Apply filters to both
#     if search:
#         temp_qs = temp_qs.filter(tran_user__icontains=search)
#         main_qs = main_qs.filter(tran_user__icontains=search)

#     if start_date:
#         temp_qs = temp_qs.filter(tran_date__date__gte=start_date)
#         main_qs = main_qs.filter(tran_date__date__gte=start_date)

#     if end_date:
#         temp_qs = temp_qs.filter(tran_date__date__lte=end_date)
#         main_qs = main_qs.filter(tran_date__date__lte=end_date)

#     # 🔹 Combine querysets
#     combined = list(chain(temp_qs, main_qs))
#     # 🔹 Sort by tran_id descending (latest first)
#     combined.sort(key=lambda x: x.tran_id)

#     # 🔹 Pagination
#     per_page = int(request.GET.get("per_page", 15))
#     paginator = Paginator(combined, per_page)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)

#     # 🔹 Other context
#     per_page_options = [15, 30, 50, 100, 500]
#     stores = Stores.objects.all()
#     tran_head = TransactionHeads.objects.all()

#     context = {
#         'data': page_obj,              
#         'status_filter': status_filter,
#         'search': search,
#         'start_date': start_date,
#         'end_date': end_date,
#         'per_page': per_page,
#         'per_page_options': per_page_options,
#         'paginator': paginator,
#         'page_number': page_number,
#         'stores': stores,
#         'tran_head': tran_head,
#     }

#     return render(request, 'pharmacy/transaction/pharmacypurchase/medicine_list.html', context)


# def medicine_list(request):
#     # 🔹 Get filters from GET parameters
#     status_filter = request.GET.get('status', '')
#     search = request.GET.get('search', '')
#     start_date = request.GET.get('start_date', '')
#     end_date = request.GET.get('end_date', '')
    

#     # 🔹 Base queryset: only PURCHASE transactions
#     data = TransactionMainsTemps.objects.all().order_by('tran_id')
#     # data = TransactionDetailsTemps.objects.filter(status=1).order_by('tran_id')
#     status_filter = request.GET.get('status')

#     if status_filter in ['1', '0']:
#         data = data.filter(status=int(status_filter))

#     if search:
#         data = data.filter(user_name__icontains=search)

#     if start_date:
#         data = data.filter(tran_date__date__gte=start_date)
#     if end_date:
#         data = data.filter(tran_date__date__lte=end_date)

#     # 🔹 Pagination
#     per_page = int(request.GET.get("per_page", 15))
#     paginator = Paginator(data, per_page)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)

#     # 🔹 Per-page options for dropdown
#     per_page_options = [15, 30, 50, 100, 500]
#     stores = Stores.objects.all()
#     tran_head = TransactionHeads.objects.all()
#     context = {
#         'data': page_obj,              # paginated data
#         'status_filter': status_filter,
#         'search': search,
#         'start_date': start_date,
#         'end_date': end_date,
#         'per_page': per_page,
#         'per_page_options': per_page_options,
#         'paginator': paginator,
#         'page_number': page_number,
#         'stores': stores,
#         'tran_head': tran_head,
#     }

#     return render(request, 'pharmacy/transaction/pharmacypurchase/medicine_list.html', context)


def medicine_list(request):
    status_filter = request.GET.get('status', '2')  # default VERIFIED
    search = request.GET.get('search', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    # 🔹 ONLY TRA transactions (PHARMACY)
    qs = TransactionMains.objects.filter(tran_id__startswith="TRA")

    # 🔹 Status filter
    if status_filter:
        qs = qs.filter(status=int(status_filter))

    # 🔹 Search
    if search:
        qs = qs.filter(tran_user__icontains=search)

    # 🔹 Date filter
    if start_date:
        qs = qs.filter(tran_date__date__gte=start_date)

    if end_date:
        qs = qs.filter(tran_date__date__lte=end_date)

    # 🔹 Latest first
    qs = qs.order_by('id')

    # 🔹 Pagination
    per_page = int(request.GET.get("per_page", 15))
    paginator = Paginator(qs, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'data': page_obj,
        'status_filter': status_filter,
        'search': search,
        'start_date': start_date,
        'end_date': end_date,
        'per_page': per_page,
        'per_page_options': [15, 30, 50, 100, 500],
        'stores': Stores.objects.all(),
        'tran_head': TransactionHeads.objects.all(),
    }

    return render(
        request,
        'pharmacy/transaction/pharmacypurchase/medicine_list.html',
        context
    )




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
                m.manufacturer_name AS manufacturer,
                f.form_name AS form,
                t.quantity,                
                t.mrp
            FROM transaction__heads t
            LEFT JOIN item__manufacturers m ON t.manufacturer_id = m.id
            LEFT JOIN item__forms f ON t.form_id = f.id
            LEFT JOIN transaction__groupes tg ON t.groupe_id = tg.id
            LEFT JOIN transaction__main__heads tmh ON tmh.id = tg.tran_groupe_type
            WHERE tmh.id = 6
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
                m.manufacturer_name AS manufacturer,
                f.form_name AS form,
                t.quantity,                
                t.mrp
            FROM transaction__heads t
            LEFT JOIN item__manufacturers m ON t.manufacturer_id = m.id
            LEFT JOIN item__forms f ON t.form_id = f.id
            LEFT JOIN transaction__groupes tg ON t.groupe_id = tg.id
            LEFT JOIN transaction__main__heads tmh ON tmh.id = tg.tran_groupe_type
            WHERE t.tran_head_name LIKE %s AND tmh.id = 6
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
    return render(request, 'pharmacy/transaction/pharmacypurchase/add.html', {'stores': stores})

def get_stores(request):
    stores = Stores.objects.filter(status=1).order_by('store_name')
    data = [
        {"id": s.id, "name": s.store_name}
        for s in stores
    ]
    return JsonResponse({"stores": data})

def get_tran_head(request):
    tran_head = TransactionHeads.objects.filter(status=1).order_by('id')  # safer
    data = [{"id": t.id, "name": t.tran_head_name} for t in tran_head]
    return JsonResponse({"tran_head": data})
from django.db import connection

def get_tran_head_name(tran_head_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT tran_head_name
            FROM transaction__heads
            WHERE id = %s
        """, [tran_head_id])
        row = cursor.fetchone()
        if row:
            return row[0]
        return ""


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

# @csrf_exempt
# def create_transaction_temp(request):
#     if request.method != "POST":
#         return JsonResponse({"success": False, "message": "Invalid request"}, status=405)

#     try:
#         with transaction.atomic():

#             # 1️⃣ Transaction ID generation
#             tran_type_with_id = 6  # Pharmacy ID
#             tran_type = tran_type_with_id  # use same for tran_type

#             last_tran = TransactionMains.objects.filter(tran_type=tran_type).order_by('-id').first()
#             last_number = 0
#             if last_tran:
#                 try:
#                     last_number = int(last_tran.tran_id[3:])
#                 except ValueError:
#                     last_number = 0
#             new_number = last_number + 1
#             tran_id = f"TRA{new_number:09d}"  # TRA000000001

#             # 2️⃣ Get POST data
#             bill_amount = float(request.POST.get("bill_amount") or 0)
#             discount = float(request.POST.get("discount") or 0)
#             quantity = float(request.POST.get("quantity") or 0)
#             net_amount = float(request.POST.get("net_amount") or 0)
#             payment = float(request.POST.get("payment") or 0)
#             due = float(request.POST.get("due") or 0)
#             store_id = request.POST.get("store_id")
#             supplier = request.POST.get("supplier")
#             tran_method = request.POST.get("tran_method")
#             location_name = request.POST.get("location")
#             tran_head = request.POST.get("tran_head")
#             tran_head_id = int(tran_head) if tran_head else None

#             if not store_id:
#                 return JsonResponse({"success": False, "message": "Store required"}, status=400)
#             store = Stores.objects.get(id=store_id)

#             # 3️⃣ Location
#             location = LocationInfos.objects.filter(division__iexact=location_name).first()
#             loc_id = location.id if location else None

#             # 4️⃣ Create TransactionMains
#             main_tran = TransactionMains.objects.create(
#                 tran_id=tran_id,
#                 tran_type=tran_type,
#                 tran_method=tran_method,
#                 tran_user=supplier,
#                 store=store,
#                 loc_id=loc_id,
#                 tran_date=timezone.now(),
#                 status=1,
#                 invoice=bill_amount,
#                 bill_amount=bill_amount,
#                 discount=discount,
#                 net_amount=net_amount,
#                 payment=payment,
#                 due=due,
#                 tran_type_with_id=tran_type_with_id
#             )
#             medicines_json = request.POST.get("medicines", "[]")
#             medicines = json.loads(medicines_json)

#             # 5️⃣ Create TransactionDetails
#             cp_value = None
#             if tran_head_id:
#                 try:
#                     head_obj = TransactionHeads.objects.get(id=tran_head_id)
#                     cp_value = head_obj.cp
#                 except TransactionHeads.DoesNotExist:
#                     cp_value = None

#             for med in medicines:
#                 TransactionDetails.objects.create(
#                     tran_id=tran_id,
#                     tran_type=tran_type,
#                     tran_method=tran_method,
#                     loc_id=loc_id,
#                     invoice=bill_amount,
#                     tran_user=supplier,
#                     amount=med.get("total", 0),
#                     discount=discount,
#                     receive=payment,
#                     payment=payment,
#                     due=due,
#                     store=store,
#                     status=1,
#                     tran_date=timezone.now(),
#                     quantity=med.get("qty", 0),
#                     tran_head_id=tran_head_id,
#                     quantity_actual=0,
#                     quantity_issue=0,
#                     quantity_return=0,
#                     tot_amount=med.get("total", 0),
#                     cp=med.get("cp", 0),
#                     mrp=None,
#                     tran_type_with_id=tran_type_with_id,
#                     product_id=med.get("product_id")  # add if you have product_id field
#                 )

#             # 6️⃣ Prepare response
#             response_data = {
#                 "id": main_tran.id,
#                 "tran_id": main_tran.tran_id,
#                 "user_name": getattr(main_tran, 'user_name', supplier),
#                 "bill_amount": main_tran.bill_amount,
#                 "discount": main_tran.discount,
#                 "net_amount": main_tran.net_amount,
#                 "payment": main_tran.payment,
#                 "due": main_tran.due,
#                 "due_col": getattr(main_tran, 'due_col', 0),
#                 "due_disc": getattr(main_tran, 'due_disc', 0),
#                 "status": main_tran.status
#             }

#             rows_per_page = int(request.GET.get('rows', 15))
#             total = TransactionMains.objects.count()
#             last_page = ceil(total / rows_per_page)

#             return JsonResponse({
#                 "success": True,
#                 "tran_id": tran_id,
#                 "data": response_data,
#                 "last_page": last_page
#             })

#     except Exception as e:
#         print("🔥 TRANSACTION ERROR:", e)
#         return JsonResponse({"success": False, "error": str(e)}, status=500)



# @csrf_exempt   # AJAX hole thakbe, na hole CSRF use koro
# def create_transaction_temp(request):
#     if request.method != "POST":
#         return JsonResponse({"success": False, "message": "Invalid request"}, status=405)

#     try:
#         with transaction.atomic():  # 🔑 ensures atomic DB operation

#             # Generate new transaction ID
#             last_tran = TransactionMainsTemps.objects.order_by('-id').first()
#             last_number = int(last_tran.tran_id[3:]) if last_tran else 0
#             new_number = last_number + 1
#             tran_id = f"TRA{new_number:09d}"  # total 12 digits

#             # Get POST data
#             bill_amount = float(request.POST.get("bill_amount") or 0)
#             discount = float(request.POST.get("discount") or 0)
#             quantity = float(request.POST.get("quantity") or 0)
#             net_amount = float(request.POST.get("net_amount") or 0)
#             payment = float(request.POST.get("payment") or 0)
#             due = float(request.POST.get("due") or 0)
#             store_id = request.POST.get("store_id")
#             supplier = request.POST.get("supplier")
#             tran_method = request.POST.get("tran_method")
#             location_name = request.POST.get("location")
#             tran_head = request.POST.get("tran_head")
#             tran_head_id = int(tran_head) if tran_head else None
#             # Validate store
#             if not store_id:
#                 return JsonResponse({"success": False, "message": "Store required"}, status=400)
#             store = Stores.objects.get(id=store_id)

#             # Location
#             location = LocationInfos.objects.filter(division__iexact=location_name).first()
#             loc_id = location.id if location else None

#             # Transaction type
#             tran_type_obj = TransactionMainHeads.objects.filter(type_name__iexact="Pharmacy").first()
#             if not tran_type_obj:
#                 return JsonResponse({"success": False, "message": "Invalid transaction type"}, status=400)
#             tran_type = tran_type_obj.id

#             # 🔹 TABLE 1: transaction_mains_temps
#             main_tran = TransactionMainsTemps.objects.create(
#                 tran_id=tran_id,
#                 tran_type=tran_type,
#                 tran_method=tran_method,
#                 tran_user=supplier,
#                 store=store,
#                 loc_id=loc_id,
#                 tran_date=timezone.now(),
#                 status=1,
#                 invoice=bill_amount,
#                 bill_amount=bill_amount,
#                 discount=discount,
#                 net_amount=net_amount,
#                 payment=payment,
#                 due=due
#             )

#             # 🔹 TABLE 2: transaction_details_temp (empty product row)
#             head_obj = None
#             cp_value = None
#             if tran_head_id:
#                 try:
#                     head_obj = TransactionHeads.objects.get(id=tran_head_id)
#                     cp_value = head_obj.cp
#                 except TransactionHeads.DoesNotExist:
#                     cp_value = None

#             TransactionDetailsTemps.objects.create(
#                 tran_id=tran_id,
#                 tran_type=tran_type,
#                 tran_method=tran_method,
#                 loc_id=loc_id,
#                 invoice=bill_amount,
#                 tran_user=supplier,
#                 amount=bill_amount,
#                 discount=discount,
#                 receive=payment,
#                 payment=payment,
#                 due=due,
#                 store=store,
#                 status=1,
#                 tran_date=timezone.now(),
#                 quantity=quantity,
#                 # product fields set to null/defaults
#                 tran_head_id=tran_head_id,
#                 quantity_actual=0,
#                 quantity_issue=0,
#                 quantity_return=0,
#                 tot_amount=net_amount,
#                 cp=cp_value,
#                 mrp=None
#             )

#             # Prepare response safely
#             response_data = {
#                 "id": main_tran.id,
#                 "tran_id": main_tran.tran_id,
#                 "user_name": getattr(main_tran, 'user_name', supplier),
#                 "bill_amount": main_tran.bill_amount,
#                 "discount": main_tran.discount,
#                 "net_amount": main_tran.net_amount,
#                 "payment": main_tran.payment,
#                 "due": main_tran.due,
#                 "due_col": getattr(main_tran, 'due_col', 0),
#                 "due_disc": getattr(main_tran, 'due_disc', 0),
#                 "status": main_tran.status
#             }

#             rows_per_page = int(request.GET.get('rows', 15))  # frontend theke rows per page, default 15
#             total = TransactionMainsTemps.objects.count()
#             last_page = ceil(total / rows_per_page)

#             return JsonResponse({"success": True, "tran_id": tran_id, "data": response_data, "last_page": last_page })

#     # except Stores.DoesNotExist:
#     #     return JsonResponse({"success": False, "message": "Invalid store"}, status=400)
#     except Exception as e:
#         print("🔥 TRANSACTION ERROR:", e)
#         return JsonResponse({"success": False, "error": str(e)}, status=500)

# GET → fetch temp transaction


@csrf_exempt
def create_transaction_temp(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"}, status=405)

    try:
        with transaction.atomic():

            # 1️⃣ Transaction ID generation
            tran_type_with_id = 6  # Pharmacy
            tran_type = tran_type_with_id

            last_tran = TransactionMains.objects.filter(tran_type=tran_type).order_by('-id').first()
            last_number = 0
            if last_tran:
                try:
                    last_number = int(last_tran.tran_id[3:])
                except ValueError:
                    last_number = 0
            new_number = last_number + 1
            tran_id = f"TRA{new_number:09d}"

            # 2️⃣ Get POST data
            bill_amount = float(request.POST.get("bill_amount") or 0)
            discount = float(request.POST.get("discount") or 0)
            quantity = float(request.POST.get("quantity") or 0)
            net_amount = float(request.POST.get("net_amount") or 0)
            payment = float(request.POST.get("payment") or 0)
            due = float(request.POST.get("due") or 0)
            store_id = request.POST.get("store_id")
            supplier = request.POST.get("supplier")
            tran_method = request.POST.get("tran_method")
            location_name = request.POST.get("location")
            tran_head = request.POST.get("tran_head")
            tran_head_id = int(tran_head) if tran_head else None

            if not store_id:
                return JsonResponse({"success": False, "message": "Store required"}, status=400)
            store = Stores.objects.get(id=store_id)

            # 3️⃣ Location
            location = LocationInfos.objects.filter(division__iexact=location_name).first()
            loc_id = location.id if location else None

            # 4️⃣ Create TransactionMains
            main_tran = TransactionMains.objects.create(
                tran_id=tran_id,
                tran_type=tran_type,
                tran_method=tran_method,
                tran_user=supplier,
                store=store,
                loc_id=loc_id,
                tran_date=timezone.now(),
                status=1,
                invoice=bill_amount,
                bill_amount=bill_amount,
                discount=discount,
                net_amount=net_amount,
                payment=payment,
                due=due,
                tran_type_with_id=tran_type_with_id
            )

            # 5️⃣ Create TransactionDetails for each medicine
            medicines_json = request.POST.get("medicines", "[]")
            medicines = json.loads(medicines_json)

            for med in medicines:
                TransactionDetails.objects.create(
                    tran_id=tran_id,
                    tran_type=tran_type,
                    tran_method=tran_method,
                    loc_id=loc_id,
                    invoice=bill_amount,
                    tran_user=supplier,
                    amount=sum(med.get("total", 0) for med in medicines),
                    discount=discount,
                    receive=payment,
                    payment=payment,
                    due=due,
                    store=store,
                    status=1,
                    tran_date=timezone.now(),
                    quantity=med.get("qty", 0),
                    tran_head_id=med.get("tran_head_id"), 
                    quantity_actual=0,
                    quantity_issue=0,
                    quantity_return=0,
                    tot_amount=med.get("total", 0),
                    cp=med.get("cp", 0),
                    mrp=None,
                    tran_type_with_id=tran_type_with_id
                    
                )

            # 6️⃣ Prepare response
            response_data = {
                "id": main_tran.id,
                "tran_id": main_tran.tran_id,
                "user_name": getattr(main_tran, 'user_name', supplier),
                "bill_amount": main_tran.bill_amount,
                "discount": main_tran.discount,
                "net_amount": main_tran.net_amount,
                "payment": main_tran.payment,
                "due": main_tran.due,
                "status": main_tran.status
            }

            rows_per_page = int(request.GET.get('rows', 15))
            total = TransactionMains.objects.count()
            last_page = ceil(total / rows_per_page)

            return JsonResponse({
                "success": True,
                "tran_id": tran_id,
                "data": response_data,
                "last_page": last_page
            })

    except Exception as e:
        print("🔥 TRANSACTION ERROR:", e)
        return JsonResponse({"success": False, "error": str(e)}, status=500)
    
@csrf_exempt
def get_transaction_main(request):
    tran_id = request.GET.get("id")
    if not tran_id:
        return JsonResponse({"success": False, "message": "Transaction ID required"}, status=400)

    try:
        with connection.cursor() as cursor:
            # 1️⃣ Fetch main transaction safely
            cursor.execute("""
                SELECT id, loc_id, tran_user, bill_amount, discount, net_amount,
                       payment, due, tran_date, store_id, tran_method
                FROM transaction__mains
                WHERE tran_id = %s
                LIMIT 1
            """, [tran_id])
            main_tran = cursor.fetchone()

        if not main_tran:
            return JsonResponse({"success": False, "message": "Transaction not found"})

        # Map main_tran columns safely
        main_data = {
            "id": main_tran[0],
            "location": main_tran[1] if main_tran[1] is not None else "",
            "supplier": main_tran[2] if main_tran[2] is not None else "",
            "bill_amount": float(main_tran[3] or 0),
            "discount": float(main_tran[4] or 0),
            "net_amount": float(main_tran[5] or 0),
            "payment": float(main_tran[6] or 0),
            "due": float(main_tran[7] or 0),
            "tran_date": main_tran[8].isoformat() if main_tran[8] else "",
            "store_id": main_tran[9] if main_tran[9] else None,
            "tran_method": main_tran[10] if main_tran[10] else ""
        }

        # 2️⃣ Fetch transaction details
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT tran_head_id, quantity, cp, tot_amount
                FROM transaction__details
                WHERE tran_id = %s
            """, [tran_id])
            details_rows = cursor.fetchall()

        details_list = []
        for d in details_rows:
            tran_head_id = d[0]
            details_list.append({
                "tran_head_id": tran_head_id,
                "name": get_tran_head_name(tran_head_id),
                "qty": float(d[1] or 0),
                "cp": float(d[2] or 0)
                # "total": float(d[3] or 0)
            })

        main_data["details"] = details_list

        return JsonResponse({"success": True, "data": main_data})

    except Exception as e:
        import traceback
        traceback.print_exc()  # Print full error to console
        return JsonResponse({"success": False, "error": str(e)}, status=500)



@csrf_exempt
def verify_transaction(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"}, status=405)

    tran_id = request.POST.get("tran_id")
    if not tran_id:
        return JsonResponse({"success": False, "message": "Transaction ID missing"}, status=400)

    try:
        with transaction.atomic():
            # 1️⃣ Fetch main transaction
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, status
                    FROM transaction__mains
                    WHERE tran_id = %s
                    LIMIT 1
                """, [tran_id])
                main_tran = cursor.fetchone()

            if not main_tran:
                return JsonResponse({
                    "success": False,
                    "message": "Transaction not found"
                }, status=404)

            main_id, main_status = main_tran

            if main_status == 2:
                return JsonResponse({
                    "success": False,
                    "message": "Transaction already verified"
                })

            # 2️⃣ Fetch transaction details
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT tran_head_id, quantity, cp
                    FROM transaction__details
                    WHERE tran_id = %s
                """, [tran_id])
                details_rows = cursor.fetchall()

            if not details_rows:
                return JsonResponse({
                    "success": False,
                    "message": "No medicines found for this transaction"
                }, status=400)

            # 3️⃣ Update stock for each medicine
            for tran_head_id, quantity, cp in details_rows:
                if tran_head_id:
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            UPDATE transaction__heads
                            SET quantity = quantity + %s,
                            cp = %s
                            WHERE id = %s
                        """, [quantity or 0, cp or 0, tran_head_id])

            # 4️⃣ Mark main transaction as verified (status=2)
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE transaction__mains
                    SET status = 2
                    WHERE id = %s
                """, [main_id])

            # 5️⃣ Mark details as verified (status=2)
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE transaction__details
                    SET status = 2
                    WHERE tran_id = %s
                """, [tran_id])
            


            # 6️⃣ Return response
            return JsonResponse({
                "success": True,
                "main_id": main_id,
                "tran_id": tran_id,
                "status": 2
            })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            "success": False,
            "message": str(e)
        }, status=500)




    
    # delete
@csrf_exempt
def delete_transaction(request, tran_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method"})

    try:
        # Delete transaction details first
        TransactionDetails.objects.filter(tran_id=tran_id).delete()
        # Delete main transaction
        TransactionMains.objects.filter(tran_id=tran_id).delete()

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

def get_transaction_for_edit(request, tran_id):
    main = TransactionMains.objects.get(tran_id=tran_id)
    details = TransactionDetails.objects.filter(tran_id=tran_id)

    medicines = []
    for d in details:
        medicines.append({
            "tran_head_id": d.tran_head_id,
            "name": d.batch_id,   # or product name field
            "qty": d.quantity,
            "cp": d.cp,
            "total": d.tot_amount
        })

    return JsonResponse({
        "tran_id": main.tran_id,
        "store": main.store_id,
        "location": main.loc_id,
        "supplier": main.tran_user,
        "tran_method": main.tran_method,
        "date": main.tran_date.strftime("%Y-%m-%d"),
        "invoice": main.bill_amount,
        "discount": main.discount,
        "net": main.net_amount,
        "payment": main.payment,
        "due": main.due,
        "medicines": medicines
    })

def update_transaction(request):
    tran_id = request.POST.get("tran_id")

    TransactionMains.objects.filter(tran_id=tran_id).update(
        store_id=request.POST.get("store_id"),
        loc_id=request.POST.get("location"),
        tran_user=request.POST.get("supplier"),
        tran_method=request.POST.get("tran_method"),
        bill_amount=request.POST.get("bill_amount"),
        discount=request.POST.get("discount"),
        net_amount=request.POST.get("net_amount"),
        payment=request.POST.get("payment"),
        due=request.POST.get("due"),
    )

    # delete old details
    TransactionDetails.objects.filter(tran_id=tran_id).delete()

    medicines = json.loads(request.POST.get("medicines", "[]"))

    for med in medicines:
        TransactionDetails.objects.create(
            tran_id=tran_id,
            tran_head_id=med["tran_head_id"],
            quantity=med["qty"],
            cp=med["cp"],
            tot_amount=med["total"],
            status=1,
            tran_date=timezone.now()
        )

    return JsonResponse({"success": True})

