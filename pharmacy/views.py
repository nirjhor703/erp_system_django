from datetime import timezone
from io import BytesIO
import json
from django.http import HttpResponse, JsonResponse
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404, redirect, render
from .models import TransactionDetails, TransactionMains,UserInfos, TransactionWiths, TransactionHeads, Stores, ItemManufacturers, LocationInfos, TransactionMainsTemps, TransactionDetailsTemps, TransactionMainHeads
from django.core.paginator import Paginator
from django.db import connection
from django.db import transaction
from django.db.models import F, Q
from django.db.models import Count, Case, When, IntegerField, Q
from datetime import datetime
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from django.template.loader import get_template
from reportlab.platypus import Table
from django.utils.dateparse import parse_date
from reportlab.platypus import Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


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

def medicine_list(request):
    # 🔹 Get filters from GET parameters
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    # 🔹 Base queryset: only PURCHASE transactions
    data = TransactionMainsTemps.objects.all().order_by('tran_id')
    status_filter = request.GET.get('status')

    if status_filter in ['1', '0']:
        data = data.filter(status=int(status_filter))

    if search:
        data = data.filter(user_name__icontains=search)

    if start_date:
        data = data.filter(tran_date__date__gte=start_date)
    if end_date:
        data = data.filter(tran_date__date__lte=end_date)

    # 🔹 Pagination
    per_page = int(request.GET.get("per_page", 15))
    paginator = Paginator(data, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 🔹 Per-page options for dropdown
    per_page_options = [15, 30, 50, 100, 500]
    stores = Stores.objects.all()
    context = {
        'data': page_obj,              # paginated data
        'status_filter': status_filter,
        'search': search,
        'start_date': start_date,
        'end_date': end_date,
        'per_page': per_page,
        'per_page_options': per_page_options,
        'paginator': paginator,
        'page_number': page_number,
        'stores': stores,
    }

    return render(request, 'pharmacy/medicine_list.html', context)



def medicine_add(request):
    # Add Medicine modal/page
    return render(request, 'pharmacy/add.html')


def product_search(request):
    q = request.GET.get('q', '').strip()
    offset = int(request.GET.get('offset', 0))
    limit = 10

    cursor = connection.cursor()

    # If no search text → show all
    if q:
        # Search by name startswith
        sql = """
            SELECT 
                t.id,
                t.tran_head_name AS name,
                t.cp,
                m.manufacturer_name AS manufacturer,
                f.form_name AS form,
                c.category_name,
                t.quantity,
                t.mrp
            FROM transaction__heads t
            LEFT JOIN item__manufacturers m ON t.manufacturer_id = m.id
            LEFT JOIN item__forms f ON t.form_id = f.id
            LEFT JOIN item__categories c ON t.category_id = c.id
            LEFT JOIN transaction__groupes tg ON t.groupe_id = tg.id
            LEFT JOIN transaction__main__heads tmh ON tmh.id = tg.tran_groupe_type
            WHERE t.tran_head_name LIKE %s
            AND (tmh.id = %s OR tmh.id IS NULL)
            ORDER BY t.id ASC
            LIMIT %s OFFSET %s
        """
        params = [f"{q}%", 6, limit, offset]

    else:
        sql = """
            SELECT 
                t.id,
                t.tran_head_name AS name,
                t.cp,
                m.manufacturer_name AS manufacturer,
                f.form_name AS form,
                c.category_name,
                t.quantity,                
                t.mrp
            FROM transaction__heads t
            LEFT JOIN item__manufacturers m ON t.manufacturer_id = m.id
            LEFT JOIN item__forms f ON t.form_id = f.id
            LEFT JOIN item__categories c ON t.category_id = c.id
            LEFT JOIN transaction__groupes tg ON t.groupe_id = tg.id
            LEFT JOIN transaction__main__heads tmh ON tmh.id = tg.tran_groupe_type
            WHERE tmh.id = 6
            ORDER BY t.id
            LIMIT %s OFFSET %s
        """
        params = [limit, offset]

    cursor.execute(sql, params)
    data = dictfetchall(cursor)

    print("SQL",sql)
    return JsonResponse({'results': data})

def purchase_list(request):
    # return render(request, 'pharmacy/medicine_list.html')
    return render(request, 'pharmacy/purchase_list.html')

def issue_list(request):
    return render(request, 'pharmacy/issue_list.html')

def order_list(request):
    return render(request, 'pharmacy/order_list.html')

def purchase_list_load(request):
    q = request.GET.get('q', '').strip()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    offset = int(request.GET.get('offset', 0))
    limit = 50

    sql = """
        SELECT 
            m.id,
            m.tran_id AS tran_id,
            m.tran_date AS tran_date,
            m.tran_type_with AS tran_type_with,
            m.tran_user AS tran_user,
            m.bill_amount AS bill_total,
            m.discount AS discount,
            m.net_amount AS net_total,
            m.receive AS advance,
            m.due_col AS due_collection,
            m.due_disc AS due_discount,
            m.due AS due
        FROM transaction__mains m
        WHERE 1=1
    """

    params = []

    # 🔥 SEARCH (optional)
    if q:
        sql += " AND (m.tran_id LIKE %s OR m.tran_user LIKE %s)"
        params.append(f"%{q}%")
        params.append(f"%{q}%")
    sql += " AND m.tran_id LIKE %s"
    params.append("PHR%")

    # 🔥 DATE FILTER (ALWAYS WORKS)
    if start_date:
        sql += " AND DATE(m.tran_date) >= %s"
        params.append(start_date)

    if end_date:
        sql += " AND DATE(m.tran_date) <= %s"
        params.append(end_date)

    sql += " ORDER BY m.id ASC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    cursor = connection.cursor()
    cursor.execute(sql, params)
    data = dictfetchall(cursor)

    return JsonResponse({'results': data})

def purchase_report_pdf(request):

    q = request.GET.get('q', '')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    sql = """
        SELECT 
            m.tran_id,
            m.tran_date,
            m.tran_type_with,
            m.tran_user,
            m.bill_amount,
            m.discount,
            m.net_amount,
            m.receive,
            m.due_col,
            m.due_disc,
            m.due
        FROM transaction__mains m
        WHERE 1=1
    """

    params = []

    if q:
        sql += " AND (m.tran_id LIKE %s OR m.tran_user LIKE %s)"
        params += [f"%{q}%", f"%{q}%"]
    sql += " AND m.tran_id LIKE %s"
    params.append("PHR%")

    if start_date:
        sql += " AND DATE(m.tran_date) >= %s"
        params.append(start_date)

    if end_date:
        sql += " AND DATE(m.tran_date) <= %s"
        params.append(end_date)

    sql += " ORDER BY m.id ASC"
    

    cursor = connection.cursor()
    cursor.execute(sql, params)
    data = dictfetchall(cursor)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    styles = getSampleStyleSheet()
    title_style = styles["Title"]
    normal_style = styles["Normal"]

    elements = []

    # =========================
    # HEADER
    # =========================
    title = Paragraph("Purchase List Report", title_style)
    elements.append(title)
    elements.append(Spacer(1, 10))

    date_text = f"""
    <b>Start Date:</b> {start_date if start_date else '-'}  
    <b>End Date:</b> {end_date if end_date else '-'}
    """

    date_para = Paragraph(date_text, normal_style)
    elements.append(date_para)
    elements.append(Spacer(1, 20))

    # =========================
    # TABLE DATA
    # =========================
    table_data = [
        ["SL","Tran ID","Date","Supplier","Tran User","Bill","Disc","Net","Adv","Due Col","Due Disc","Due"]
    ]

    for i, p in enumerate(data, 1):
        table_data.append([
            i,
            p["tran_id"],
            str(p["tran_date"]),
            p["tran_type_with"],
            p["tran_user"],
            
            p["bill_amount"],
            p["discount"],
            p["net_amount"],
            p["receive"],
            p["due_col"],
            p["due_disc"],
            p["due"]
        ])

    table = Table(table_data)

    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
    ]))

    elements.append(table)

    # =========================
    # BUILD PDF
    # =========================
    doc.build(elements)

    buffer.seek(0)
    return HttpResponse(buffer, content_type="application/pdf")


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


def get_divisions_combo(request):

    cursor = connection.cursor()

    sql = """
        SELECT
        MIN(loc.id) AS id,
        loc.division
        FROM location__infos loc
        GROUP BY loc.division
        ORDER BY loc.division;
    """
    params = []

    cursor.execute(sql, params)
    data = dictfetchall(cursor)
    print("DEBUG",data)

    return JsonResponse({
        "divisions_combo": data
    }, safe=False)

def get_supplier_combo(request):

    cursor = connection.cursor()

    sql = """
        SELECT
        m.id AS id,
        m.manufacturer_name
        FROM item__manufacturers m
        ORDER BY m.manufacturer_name;
    """
    params = []

    cursor.execute(sql, params)
    data = dictfetchall(cursor)
    print("DEBUG",data)

    return JsonResponse({
        "supplier_combo": data
    })

def get_store_combo(request):

    cursor = connection.cursor()

    sql = """
        SELECT
        s.id AS id,
        s.store_name
        FROM stores s
        ORDER BY s.store_name;
    """
    params = []

    cursor.execute(sql, params)
    data = dictfetchall(cursor)
    print("DEBUG",data)

    return JsonResponse({
        "store_combo": data
    })

def get_transaction_with_combo(request):
    data = TransactionWiths.objects.filter(
        tran_type=6,
        tran_method='payment',
        status=1
    ).values('id', 'tran_with_name')

    return JsonResponse(list(data), safe=False)

def get_transaction_with_combo_issue(request):
    data = TransactionWiths.objects.filter(
        tran_type=6,
        tran_method='receive',
        status=1
    ).values('id', 'tran_with_name')

    return JsonResponse(list(data), safe=False)

def get_supplier_by_tran_with(request):
    tran_with_id = request.GET.get('tran_with_id')

    if not tran_with_id:
        return JsonResponse([], safe=False)

    data = list(UserInfos.objects.filter(
        tran_user_type_id=int(tran_with_id),   # 🔥 FIX HERE
        tran_user_type__tran_type=6
    ).values('id', 'user_name'))
    print("tran_with_id:", tran_with_id, type(tran_with_id))
    return JsonResponse(data, safe=False)


def add_purchase_page(request):
    return render(request, 'pharmacy/add_4.html')

def add_issue_page(request):
    return render(request, 'pharmacy/issue.html')

def add_order_page(request):
    return render(request, 'pharmacy/order.html')

@csrf_exempt   # AJAX hole thakbe, na hole CSRF use koro
def create_transaction_temp(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"}, status=405)

    try:
        with transaction.atomic():  # 🔑 ensures atomic DB operation

            # Generate new transaction ID
            last_tran = TransactionMainsTemps.objects.order_by('-id').first()
            last_number = int(last_tran.tran_id[3:]) if last_tran else 0
            new_number = last_number + 1
            tran_id = f"TRA{new_number:09d}"  # total 12 digits

            # Get POST data
            bill_amount = float(request.POST.get("bill_amount") or 0)
            discount = float(request.POST.get("discount") or 0)
            net_amount = float(request.POST.get("net_amount") or 0)
            payment = float(request.POST.get("payment") or 0)
            due = float(request.POST.get("due") or 0)
            store_id = request.POST.get("store_id")
            supplier = request.POST.get("supplier")
            tran_method = request.POST.get("tran_method")
            location_name = request.POST.get("location")

            # Validate store
            if not store_id:
                return JsonResponse({"success": False, "message": "Store required"}, status=400)
            store = Stores.objects.get(id=store_id)

            # Location
            location = LocationInfos.objects.filter(division__iexact=location_name).first()
            loc_id = location.id if location else None

            # Transaction type
            tran_type_obj = TransactionMainHeads.objects.filter(type_name__iexact="Pharmacy").first()
            if not tran_type_obj:
                return JsonResponse({"success": False, "message": "Invalid transaction type"}, status=400)
            tran_type = tran_type_obj.id

            # 🔹 TABLE 1: transaction_mains_temps
            main_tran = TransactionMainsTemps.objects.create(
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
                due=due
            )

            # 🔹 TABLE 2: transaction_details_temp (empty product row)
            TransactionDetailsTemps.objects.create(
                tran_id=tran_id,
                tran_type=tran_type,
                tran_method=tran_method,
                invoice=bill_amount,
                tran_user=supplier,
                amount=bill_amount,
                discount=discount,
                receive=payment,
                payment=payment,
                due=due,
                store=store,
                status=1,
                tran_date=timezone.now(),
                # product fields set to null/defaults
                tran_head_id=None,
                quantity_actual=0,
                quantity=0,
                quantity_issue=0,
                quantity_return=0,
                tot_amount=net_amount,
                cp=None,
                mrp=None
            )

            # Prepare response safely
            response_data = {
                "id": main_tran.id,
                "tran_id": main_tran.tran_id,
                "user_name": getattr(main_tran, 'user_name', supplier),
                "bill_amount": main_tran.bill_amount,
                "discount": main_tran.discount,
                "net_amount": main_tran.net_amount,
                "payment": main_tran.payment,
                "due": main_tran.due,
                "due_col": getattr(main_tran, 'due_col', 0),
                "due_disc": getattr(main_tran, 'due_disc', 0),
                "status": main_tran.status
            }

            return JsonResponse({"success": True, "tran_id": tran_id, "data": response_data})

    # except Stores.DoesNotExist:
    #     return JsonResponse({"success": False, "message": "Invalid store"}, status=400)
    except Exception as e:
        print("🔥 TRANSACTION ERROR:", e)
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


def get_transaction(request, tran_id):
    try:
        # 🔹 Fetch main transaction
        main = get_object_or_404(TransactionMainsTemps, tran_id=tran_id)

        # 🔹 Supplier name from tran_user
        supplier_name = ""
        if main.tran_user:
            supplier = ItemManufacturers.objects.filter(id=main.tran_user).first()
            if supplier:
                supplier_name = supplier.manufacturer_name

        # 🔹 Store info
        store_name = main.store.store_name if main.store else ""
        store_id = main.store.id if main.store else None

        # 🔹 Location
        location_name = ""
        if main.loc_id:
            loc = LocationInfos.objects.filter(id=main.loc_id).first()
            if loc:
                location_name = loc.division

        # 🔹 Transaction details
        details_qs = TransactionDetailsTemps.objects.filter(tran_id=tran_id)
        details = []
        for d in details_qs:
            # Get product name
            product_name = ""
            if d.tran_head_id:
                product = TransactionHeads.objects.filter(id=d.tran_head_id).first()
                if product:
                    product_name = product.tran_head_name
            details.append({
                "id": d.id,
                "name": product_name or "Unknown Product",
                "qty": d.quantity or 0,
                "cp": d.cp or 0,
                "total": d.tot_amount or 0,
                "unit": "PCS"  # optional, or fetch from d.unit_id if needed
            })

        # 🔹 Response
        response = {
            "success": True,
            "data": {
                "tran_id": main.tran_id,
                "supplier": supplier_name,
                "store_id": store_id,
                "store_name": store_name,
                "location": location_name,
                "tran_method": main.tran_method,
                "tran_date": main.tran_date.date().strftime("%Y-%m-%d"),
                "bill_amount": main.bill_amount or 0,
                "discount": main.discount or 0,
                "net_amount": main.net_amount or 0,
                "payment": main.payment or 0,
                "due": main.due or 0,
                "details": details
            }
        }

        return JsonResponse(response)

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})

    

# def get_temp_transaction(request, tran_id):
#     tran = TransactionMainsTemps.objects.get(id=tran_id)
#     medicines = tran.medicines.all().values("name","quantity","unit_price","total")

#     # fetch products from transaction__heads table
#     cursor = connection.cursor()
#     cursor.execute("SELECT tran_head_name AS name, '' AS generic_name, '' AS manufacture, '' AS form, quantity AS qty, cp, mrp FROM transaction__heads")
#     products = dictfetchall(cursor)

#     return JsonResponse({
#         "success": True,
#         "data": {
#             "location": tran.location,
#             "store_id": tran.store_id,
#             "date": tran.date,
#             "supplier_name": tran.supplier_name,
#             "payment_method": tran.tran_method,
#             "bill_amount": tran.bill_amount,
#             "discount": tran.discount,
#             "net_amount": tran.net_amount,
#             "payment": tran.payment,
#             "due": tran.due,
#             "medicines": list(medicines),
#             "products": products
#         }
#     })
    

    



# def get_temp_details(request, tran_id):
#     main = TransactionMainsTemps.objects.get(tran_id=tran_id)

#     items = TransactionDetailsTemps.objects.filter(tran_id=tran_id)

#     med_list = []
#     for i in items:
#         med_list.append({
#             "name": i.product_name,
#             "qty": i.qty,
#             "price": i.unit_price,
#             "total": i.total
#         })

#     return JsonResponse({
#         "tran_id": main.tran_id,
#         "store_id": main.store_id,
#         "location": main.loc_id,
#         "method": main.tran_method,
#         "bill_amount": main.bill_amount,
#         "discount": main.discount,
#         "net_amount": main.net_amount,
#         "payment": main.payment,
#         "due": main.due,
#         "medicines": med_list
#     })


@csrf_exempt  # AJAX POST

@transaction.atomic
def save_purchase(request):
    print("❌ PURCHASE API HIT")
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"}, status=405)

    try:
        data = json.loads(request.body)

        # ---- Form-level info ----
        store_id = data.get("store")
        location_id = data.get("location")
        supplier_id = data.get("supplier")
        tran_type_with = data.get("tran_type_with")
        if not tran_type_with:
         return JsonResponse({"success": False, "message": "Transaction With required"}, status=400)
        invoice = data.get("invoice")
        payment_method = data.get("payment_method")
        bill_amount = data.get("bill_amount") or 0
        discount = data.get("discount") or 0
        net_amount = data.get("net_amount") or 0
        receive = 0
        payment = data.get("payment") or 0
        due = data.get("due") or 0
        # tran_date = data.get("tran_date") or timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        tran_date = data.get("tran_date")
        # Date & Time Both

        if tran_date:
            tran_date = datetime.combine(
                datetime.strptime(tran_date, "%Y-%m-%d").date(),
                timezone.localtime().time()
            )
        else:
            tran_date = timezone.localtime()
        
        
        # Only Date
        # if tran_date:
        #     tran_date = datetime.strptime(tran_date, "%Y-%m-%d")
        #     tran_date = timezone.make_aware(tran_date)
        # else:
        #     tran_date = timezone.now()

        print("tran_date from form:", tran_date)

        products = data.get("products", [])
        if not products:
            return JsonResponse({"success": False, "message": "No products selected"}, status=400)

        # ---- Generate transaction ID ----
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT tran_id 
                FROM transaction__mains
                WHERE tran_id LIKE 'PHR%'
                ORDER BY tran_id DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()

            if row:
                last_number = int(row[0][3:])  # remove PHR
            else:
                last_number = 0

            phr_code = "PHR" + str(last_number + 1).zfill(9)
        # ---- END of Generate transaction ID ----

        tran_type = 6
        status = 1

        # ---- Insert into transaction__mains ----
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO transaction__mains
                (tran_id, tran_type, tran_method,tran_user, tran_type_with, store_id, 
                 loc_id, tran_date, status, invoice, bill_amount, discount, net_amount,
                 payment, due)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, [
                phr_code, tran_type, payment_method,supplier_id, tran_type_with, store_id,
                location_id, tran_date, status, invoice, bill_amount, 
                discount, net_amount, payment, due
            ])

        # ---- Prepare details data using index-style access ----
        details_data = []

        update_query = """
        UPDATE transaction__heads
        SET cp = %s, mrp = %s
        WHERE id = %s
        """
        update_data = []
        
        for row in products:
            details_data.append([
                # phr_code,         # tran_id
                # tran_type,        # tran_type_with
                # location_id,      # loc_id
                # store_id,         # store_id
                # tran_type_with,   # tran_user
                # row[0],           # tran_head_id
                # row[1],           # quantity_actual
                # row[1],           # quantity
                # 0,                # quantity_issue
                # 0,                # quantity_return   
                # row[4],           # cp
                # row[5],           # mrp
                # row[6],           # expiry_date
                # row[7],           # tot_amount                
                # tran_date,        # tran_date
                # status,           # status
                # discount,         # discount
                # receive,          # receive
                # receive,          # payment
                # due               # due

                phr_code,          # tran_id
                tran_type,        # tran_type_with
                payment_method,   # tran_method
                invoice,          # invoice
                location_id,      # loc_id
                tran_type_with,      # tran_user
                row[0],           # tran_head_id
                row[1],           # quantity_actual
                row[1],           # quantity
                0,                # quantity_issue
                0,                # quantity_return
                0,                # unit_id
                row[2],           # amount (cp)
                row[5],           # tot_amount
                row[2],           # cp
                row[3],           # mrp
                row[4],           # expiry_date
                store_id,         # store_id
                tran_date,        # tran_date
                status,           # status
                discount,           # discount
                0,          # receive
                payment,          # payment
                due               # due

            ])

            # update product price
            # cursor.execute(update_query, [row[2], row[3], row[0]])

            update_data.append((row[2], row[3], row[0]))

        # ✅ new cursor
        with connection.cursor() as cursor:
            cursor.executemany(update_query, update_data)

        # ---- Insert into transaction__details ----
        # query = """
        #     INSERT INTO transaction__details
        #     (tran_id, tran_type, loc_id, store_id, tran_type_with, 
        #     tran_head_id, quantity_actual, quantity, quantity_issue, quantity_return,
        #     cp, mrp, expiry_date, tot_amount,
        #     tran_date, status, discount, receive, payment, due)
        #     VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        # """        
        query = """
            INSERT INTO transaction__details
            (tran_id, tran_type, tran_method, invoice, loc_id, tran_type_with,
             tran_head_id, quantity_actual, quantity, quantity_issue, quantity_return,
             unit_id, amount, tot_amount, cp, mrp, expiry_date, store_id,
             tran_date, status, discount, receive, payment, due)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        with connection.cursor() as cursor:
            cursor.executemany(query, details_data)



        return JsonResponse({"success": True, "tran_id": phr_code})

    except Exception as e:
        print("🔥 SAVE PURCHASE ERROR:", e)
        return JsonResponse({"success": False, "error": str(e)}, status=500)
    
# @transaction.atomic
# def save_issue(request):
#     print("🔥 ISSUE API HIT")
#     if request.method != "POST":
#         return JsonResponse({"success": False, "message": "Invalid request"}, status=405)

#     try:
#         data = json.loads(request.body)

#         # ---- Form-level info ----
#         store_id = data.get("store")
#         location_id = data.get("location")
#         tran_type_with = data.get("supplier")
#         invoice = data.get("purchaseinvoice")
#         payment_method = data.get("payment_method")
#         bill_amount = data.get("bill_amount") or 0
#         discount = data.get("discount") or 0
#         net_amount = data.get("net_amount") or 0
#         receive = data.get("receive") or 0
#         due = data.get("due") or 0
#         tran_date = data.get("tran_date") or timezone.now().strftime("%Y-%m-%d %H:%M:%S")

#         products = data.get("products", [])
#         if not products:
#             return JsonResponse({"success": False, "message": "No products selected"}, status=400)

#         # ---- Generate transaction ID ----
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 SELECT tran_id 
#                 FROM transaction__mains
#                 WHERE tran_id LIKE 'PHI%'
#                 ORDER BY tran_id DESC
#                 LIMIT 1
#             """)
            
#             row = cursor.fetchone()

#             if row:
#                 last_number = int(row[0][3:])  # remove PHR
#             else:
#                 last_number = 0

#             phi_code = "PHI" + str(last_number + 1).zfill(9)
#         # ---- END of Generate transaction ID ----

#         tran_type = 6
#         status = 1

#         # ---- Insert into transaction__mains ----
#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 INSERT INTO transaction__mains
#                 (tran_id, tran_type, tran_method, tran_type_with, store_id, loc_id,
#                  tran_date, status, invoice, bill_amount, discount, net_amount,
#                  payment, due)
#                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
#             """, [
#                 phi_code, tran_type, payment_method, tran_type_with, store_id,
#                 location_id, tran_date, status, bill_amount, bill_amount,
#                 discount, net_amount, receive, due
#             ])

#         # ---- Prepare details data using index-style access ----
#         details_data = []
#         for row in products:
#             details_data.append([
#                 phi_code,         # tran_id
#                 tran_type,        # tran_type_with
#                 payment_method,   # tran_method
#                 invoice,          # invoice
#                 location_id,      # loc_id
#                 tran_type_with,   # tran_user
#                 row[0],           # tran_head_id
#                 row[1],           # quantity_actual
#                 0,                # quantity
#                 row[1],           # quantity_issue
#                 0,                # quantity_return
#                 row[5],           # unit_id
#                 row[2],           # amount (cp)
#                 row[3],           # tot_amount
#                 row[2],           # cp
#                 0,                # mrp (ignored)
#                 row[6],           # expiry_date
#                 store_id,         # store_id
#                 tran_date,        # tran_date
#                 status,           # status
#                 discount,         # discount
#                 receive,          # receive
#                 receive,          # payment
#                 due               # due
#             ])

#         # ---- Insert into transaction__details ----
#         query = """
#             INSERT INTO transaction__details
#             (tran_id, tran_type, tran_method, invoice, loc_id, tran_type_with,
#              tran_head_id, quantity_actual, quantity, quantity_issue, quantity_return,
#              unit_id, amount, tot_amount, cp, mrp, expiry_date, store_id,
#              tran_date, status, discount, receive, payment, due)
#             VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
#         """

#         with connection.cursor() as cursor:
#             cursor.executemany(query, details_data)

#         return JsonResponse({"success": True, "tran_id": phi_code})

#     except Exception as e:
#         print("🔥 SAVE PURCHASE ERROR:", e)
#         return JsonResponse({"success": False, "error": str(e)}, status=500)    



@transaction.atomic
def save_issue(request):
    print("🔥 ISSUE API HIT")
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"}, status=405)

    try:
        data = json.loads(request.body)

        # ---- Form-level info ----
        store_id = data.get("store")
        location_id = data.get("location")
        tran_type_with = data.get("tran_type_with")
        supplier_id = data.get("supplier")
        invoice = data.get("purchaseinvoice")
        tran_method = data.get("tran_method")
        bill_amount = data.get("bill_amount") or 0
        discount = data.get("discount") or 0
        net_amount = data.get("net_amount") or 0
        receive = data.get("receive") or 0
        due = data.get("due") or 0
        tran_date = data.get("tran_date")
        
        # Handle date
        if tran_date:
            tran_date = datetime.combine(
                datetime.strptime(tran_date, "%Y-%m-%d").date(),
                timezone.localtime().time()
            )
        else:
            tran_date = timezone.localtime()

        products = data.get("products", [])
        if not products:
            return JsonResponse({"success": False, "message": "No products selected"}, status=400)

        # ---- Generate transaction ID (PHI) same style as PHR ----
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT tran_id 
                FROM transaction__mains
                WHERE tran_id LIKE 'PHI%' 
                ORDER BY tran_id DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            if row:
                last_number = int(row[0][3:])  # remove PHI prefix
            else:
                last_number = 0

            # New PHI code
            phi_code = "PHI" + str(last_number + 1).zfill(9)
            print("Generated PHI code:", phi_code)

        tran_type = 6
        status = 1

        # ---- Insert into transaction__mains ----
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO transaction__mains
                (tran_id, tran_type, tran_method,tran_user,tran_type_with, store_id, loc_id,
                 tran_date, status, invoice, bill_amount, discount, net_amount,
                 payment, due)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, [
                phi_code, tran_type, tran_method,supplier_id, tran_type_with, store_id,
                location_id, tran_date, status, invoice, bill_amount,
                discount, net_amount, receive, due
            ])

        # ---- Prepare details data ----
        details_data = []
        for row in products:
                details_data.append([
                    phi_code,
                    tran_type,
                    tran_method,
                    invoice,
                    location_id,
                    tran_type_with,
                    row["tran_head_id"],
                    row["qty"],
                    0,
                    row["qty"],
                    0,
                    row.get("unit_id"),
                    row["cp"],
                    row["total"],
                    row["cp"],
                    row["mrp"],
                    row.get("expiry"),
                    store_id,
                    tran_date,
                    status,
                    discount,
                    receive,
                    0,
                    due
                ])

        # ---- Insert into transaction__details ----
        query = """
            INSERT INTO transaction__details
            (tran_id, tran_type, tran_method, invoice, loc_id, tran_type_with,
             tran_head_id, quantity_actual, quantity, quantity_issue, quantity_return,
             unit_id, amount, tot_amount, cp, mrp, expiry_date, store_id,
             tran_date, status, discount, receive, payment, due)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        with connection.cursor() as cursor:
            cursor.executemany(query, details_data)

        return JsonResponse({"success": True, "tran_id": phi_code})

    except Exception as e:
        print("🔥 SAVE ISSUE ERROR:", e)
        return JsonResponse({"success": False, "error": str(e)}, status=500)
    
def issue_invoice(request, tran_id):

    # ---- MAIN DATA ----
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT tran_id, tran_date, store_id, loc_id, tran_type_with,
                   invoice, bill_amount, discount, net_amount, payment, due
            FROM transaction__mains
            WHERE tran_id = %s
        """, [tran_id])

        main = cursor.fetchone()

    if not main:
        return HttpResponse("Invoice not found")

    # ---- DETAILS DATA ----
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                d.tran_head_id,
                d.quantity_issue,
                d.cp,
                d.mrp,
                d.tot_amount
            FROM transaction__details d
            WHERE d.tran_id = %s
        """, [tran_id])

        details = cursor.fetchall()

    # ---- PRODUCT LIST ----
    products = []
    for i, row in enumerate(details):
        products.append({
            "sl": i + 1,
            "name": row[0],   # ⚠️ ekhane name nai, id ase
            "qty": row[1],
            "cp": row[2],
            "mrp": row[3],
            "total": row[4],
        })

    context = {
        "tran_id": main[0],
        "tran_date": main[1],
        "store": main[2],
        "location": main[3],
        "supplier": main[4],
        "invoice": main[5],
        "bill_amount": main[6],
        "discount": main[7],
        "net_amount": main[8],
        "receive": main[9],
        "due": main[10],
        "products": products
    }

    return render(request, "pharmacy/issue_invoice.html", context)



def download_issue_pdf(request, tran_id):

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{tran_id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    y = height - 50

    # ================= HEADER =================
    p.setFont("Helvetica-Bold", 16)
    p.drawString(180, y, "PHARMACY ISSUE INVOICE")
    y -= 25   # reduced gap

    # ================= MAIN INFO =================
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT tran_id, tran_date, invoice, bill_amount, discount, net_amount, payment, due
            FROM transaction__mains
            WHERE tran_id = %s
        """, [tran_id])

        main = cursor.fetchone()

    if not main:
        p.drawString(50, y, "No data found")
        p.showPage()
        p.save()
        return response

    p.setFont("Helvetica", 11)
    p.drawString(50, y, f"Transaction ID: {main[0]}"); y -= 15
    p.drawString(50, y, f"Date: {main[1]}"); y -= -20

    # ================= DETAILS =================
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT tran_head_id, quantity_issue, cp, mrp, tot_amount
            FROM transaction__details
            WHERE tran_id = %s
        """, [tran_id])

        details = cursor.fetchall()

    # Table data
    table_data = [
        ["SL", "Product ID", "Qty", "CP", "MRP", "Total"]
    ]

    for i, row in enumerate(details, start=1):
        table_data.append([
            i,
            row[0],
            row[1],
            row[2],
            row[3],
            row[4]
        ])

    table = Table(table_data, colWidths=[40, 100, 60, 60, 60, 80])

    table.setStyle(TableStyle([
        # ONLY BOLD HEADER
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),

        # ALIGN CENTER
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),

        # GRID ONLY (NO COLOR)
        ('GRID', (0, 0), (-1, -1), 0.5, (0, 0, 0)),
    ]))

    # 🔥 IMPORTANT: reduced gap here
    table.wrapOn(p, 50, y)
    table.drawOn(p, 50, y - 140)

    y -= (len(details) * 16) + 160   # reduced spacing

    # ================= SUMMARY =================
    p.setFont("Helvetica-Bold", 11)

    p.drawString(50, y, f"Bill Amount: {main[3]}"); y -= 15
    p.drawString(50, y, f"Discount: {main[4]}"); y -= 15
    p.drawString(50, y, f"Net Amount: {main[5]}"); y -= 15
    p.drawString(50, y, f"Paid: {main[6]}"); y -= 15
    p.drawString(50, y, f"Due: {main[7]}"); y -= 15

    p.showPage()
    p.save()

    return response


@transaction.atomic
def save_order(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"}, status=405)

    try:
        data = json.loads(request.body)

        tran_date = data.get("tran_date")
        if tran_date:
            tran_date = datetime.strptime(tran_date, "%Y-%m-%d")
        else:
            tran_date = timezone.localtime()

        products = data.get("products", [])
        if not products:
            return JsonResponse({"success": False, "message": "No products selected"}, status=400)

        payment_method = data.get("payment_method") or "cash"
        store_id = data.get("store")
        location_id = data.get("location")
        supplier_id = data.get("supplier")
        invoice = data.get("invoice")
        bill_amount = data.get("bill_amount") or 0
        discount = data.get("discount") or 0
        net_amount = data.get("net_amount") or 0
        receive = data.get("receive") or 0
        due = data.get("bill_amount") or 0

        # ---------------- TRAN ID ----------------
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT tran_id
                FROM transaction__mains
                WHERE tran_id LIKE 'PHO%'
                ORDER BY tran_id DESC
                LIMIT 1
            """)
            row = cursor.fetchone()

            if row:
                last_number = int(row[0][3:])
            else:
                last_number = 0

            pho_code = "PHO" + str(last_number + 1).zfill(9)

        tran_type = 6
        status = 0

        # ---------------- MAIN INSERT ----------------
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO transaction__mains
                (tran_id, tran_type, tran_method, store_id, loc_id, tran_type_with,
                tran_date, status, invoice, bill_amount,
                discount, net_amount, payment, due)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, [
                pho_code,
                tran_type,
                payment_method,
                store_id,
                location_id,
                supplier_id, 
                tran_date,
                status,
                invoice,
                bill_amount,
                discount,
                net_amount,
                receive,
                due
            ])

        # ---------------- DETAILS INSERT ----------------
        details_data = []

        for row in products:
            details_data.append([
                pho_code,        # tran_id
                tran_type,       # tran_type
                payment_method,  # tran_method

                row[0],          # product_id
                row[1],          # qty
                0,               # quantity (must be 0)
                0,          # quantity_issue

                0,               # quantity_return
                row[2],          # cp
                row[3],          # total
                row[2],          # cp
                row[2],          # mrp
                tran_date,
                status,
                due
            ])

        query = """
            INSERT INTO transaction__details
            (tran_id, tran_type, tran_method,
             tran_head_id,
             quantity_actual, quantity, quantity_issue, quantity_return,
             amount, tot_amount, cp, mrp,
             tran_date, status, due)
            VALUES (%s,%s,%s,
                    %s,
                    %s,%s,%s,%s,
                    %s,%s,%s,%s,
                    %s,%s, %s)
        """

        with connection.cursor() as cursor:
            cursor.executemany(query, details_data)

        return JsonResponse({"success": True, "tran_id": pho_code})

    except Exception as e:
        print("🔥 SAVE ORDER ERROR:", e)
        return JsonResponse({"success": False, "error": str(e)}, status=500)
    
def search_po(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                tran_id,
                tran_date,
                invoice,
                net_amount
            FROM transaction__mains
            WHERE tran_id LIKE 'PHO%'   -- 🔥 IMPORTANT FILTER
            ORDER BY tran_id DESC
        """)
        rows = cursor.fetchall()

    results = []

    for r in rows:
        results.append({
            "tran_id": r[0],
            "date": r[1].strftime("%Y-%m-%d"),
            "client_name": r[2] or "",   # invoice ke client dhora hoise
            "total": float(r[3] or 0)
        })

    return JsonResponse({"results": results})

def get_po_details(request):
    po_id = request.GET.get("id")

    query = """
        SELECT 
            td.tran_head_id,
            td.quantity_actual,
            td.cp,
            td.mrp,
            th.tran_head_name,
            tm.invoice,
            tm.tran_date,
            tm.tran_method
        FROM transaction__details td
        JOIN transaction__heads th ON th.id = td.tran_head_id
        JOIN transaction__mains tm ON tm.tran_id = td.tran_id
        WHERE td.tran_id = %s
    """

    with connection.cursor() as cursor:
        cursor.execute(query, [po_id])
        rows = cursor.fetchall()

    if not rows:
        return JsonResponse({
            "invoice": "",
            "date": "",
            "payment_method": "cash",
            "products": []
        })

    products = []
    for r in rows:
        products.append({
            "id": r[0],
            "qty": r[1],
            "cp": float(r[2] or 0),
            "mrp": float(r[3] or 0),
            "name": r[4]
        })

    return JsonResponse({
        "invoice": rows[0][5],
        "date": rows[0][6],
        "payment_method": rows[0][7],
        "products": products
    })