from django.shortcuts import render
from django.http import JsonResponse
from core.models import TransactionHeads, Stores, ItemManufacturers, LocationInfos, TransactionMainsTemps, TransactionDetailsTemps
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import F, Q
from django.db.models import Count, Case, When, IntegerField, Q
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
from django.utils import timezone

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



