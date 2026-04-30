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

def product_search(request):
    q = request.GET.get('q', '').strip()
    offset = int(request.GET.get('offset', 0))
    limit = 10

    cursor = connection.cursor()

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
            JOIN transaction__groupes tg ON t.groupe_id = tg.id
            JOIN transaction__main__heads tmh ON tmh.id = tg.tran_groupe_type
            LEFT JOIN item__manufacturers m ON t.manufacturer_id = m.id
            LEFT JOIN item__forms f ON t.form_id = f.id
            LEFT JOIN item__categories c ON t.category_id = c.id
            WHERE t.tran_head_name LIKE %s
            AND tmh.id = 1
            ORDER BY t.id ASC
            LIMIT %s OFFSET %s
        """

    params = [f"{q}%", limit, offset]

    cursor.execute(sql, params)
    data = dictfetchall(cursor)

    return JsonResponse({'results': data})

def add_payment_page(request):
    return render(request, 'general_transaction/payment.html')
def payment_list(request):
    # return render(request, 'pharmacy/medicine_list.html')
    return render(request, 'general_transaction/payment_list.html')

def payment_list_load(request):
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
    params.append("GPA%")

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



def payment_report_pdf(request):

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
    params.append("GPA%")

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
    title = Paragraph("Payment List Report", title_style)
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

# def get_supplier_combo(request):

#     cursor = connection.cursor()

#     sql = """
#         SELECT
#         m.id AS id,
#         m.manufacturer_name
#         FROM item__manufacturers m
#         ORDER BY m.manufacturer_name;
#     """
#     params = []

#     cursor.execute(sql, params)
#     data = dictfetchall(cursor)
#     print("DEBUG",data)

#     return JsonResponse({
#         "supplier_combo": data
#     })

def get_transaction_with_users_combo(request):

    data = UserInfos.objects.filter(
        tran_user_type__tran_type=1,
        tran_user_type__tran_method='payment'
    ).values(
        'id',
        'user_name',
        'tran_user_type_id'
    ).order_by('user_name')

    return JsonResponse(list(data), safe=False)

# def get_user_by_tran_with_general(request):
#     tran_with_id = request.GET.get('tran_with_id')

#     if not tran_with_id:
#         return JsonResponse([], safe=False)

#     data = list(UserInfos.objects.filter(
#         tran_user_type_id=tran_with_id,
#         tran_user_type__tran_type=1
#     ).values('id', 'user_name'))

#     return JsonResponse(data, safe=False)

@csrf_exempt
@transaction.atomic
def save_general_payment(request):

    if request.method != "POST":
        return JsonResponse({"success": False}, status=405)

    try:
        data = json.loads(request.body)

        # ---- Form Data ----
        store_id = data.get("store")
        location_id = data.get("location")
        user_id = data.get("supplier")
        tran_type_with = data.get("tran_type_with")

        if not tran_type_with:
            return JsonResponse({"success": False, "message": "Transaction With required"}, status=400)

        invoice = data.get("invoice")
        payment_method = data.get("payment_method")

        bill_amount = data.get("bill_amount") or 0
        discount = data.get("discount") or 0
        net_amount = data.get("net_amount") or 0
        receive = 0   # always 0 from frontend
        payment = data.get("payment") or 0 
        due = data.get("due") or 0

        tran_date = data.get("tran_date")

        if tran_date:
            tran_date = datetime.combine(
                datetime.strptime(tran_date, "%Y-%m-%d").date(),
                timezone.localtime().time()
            )
        else:
            tran_date = timezone.localtime()

        products = data.get("products", [])

        # ---- Generate ID ----
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT tran_id 
                FROM transaction__mains
                WHERE tran_id LIKE 'GPA%'
                ORDER BY tran_id DESC
                LIMIT 1
            """)
            row = cursor.fetchone()

            last_number = int(row[0][3:]) if row else 0
            tran_id = "GPA" + str(last_number + 1).zfill(9)

        tran_type = 1   # ✅ GENERAL
        status = 1

        # ---- MAIN TABLE ----
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO transaction__mains
                (tran_id, tran_type, tran_method, tran_user, tran_type_with,
                 store_id, loc_id, tran_date, status, invoice,
                 bill_amount, discount, net_amount, payment, due)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, [
                tran_id, tran_type, payment_method, user_id, tran_type_with,
                store_id, location_id, tran_date, status, invoice,
                bill_amount, discount, net_amount, payment, due
            ])

        # ---- DETAILS ----
        details_data = []

        for row in products:
            details_data.append([
                tran_id,
                tran_type,
                payment_method,
                invoice,
                location_id,
                tran_type_with,
                row[0],   # product id
                1,   # qty
                row[1],
                0,
                0,
                0,
                row[2],   # amount
                row[5],   # total
                0,   # cp
                0,   # mrp
                row[4],   # expiry
                store_id,
                tran_date,
                status,
                discount,
                0,
                payment,
                due
            ])

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

        return JsonResponse({"success": True, "tran_id": tran_id})

    except Exception as e:
        print("🔥 GENERAL PAYMENT ERROR:", e)
        return JsonResponse({"success": False, "error": str(e)}, status=500)
    


def add_receive_page(request):
    return render(request, 'general_transaction/receive.html')
def receive_list(request):
    # return render(request, 'pharmacy/medicine_list.html')
    return render(request, 'general_transaction/receive_list.html')

def receive_list_load(request):
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
    params.append("GRE%")

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



def receive_report_pdf(request):

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
    params.append("GRE%")

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
    title = Paragraph("Receive List Report", title_style)
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

@csrf_exempt
@transaction.atomic
def save_general_receive(request):

    if request.method != "POST":
        return JsonResponse({"success": False}, status=405)

    try:
        data = json.loads(request.body)

        # ---- Form Data ----
        store_id = data.get("store")
        location_id = data.get("location")
        user_id = data.get("supplier")
        tran_type_with = data.get("tran_type_with")

        if not tran_type_with:
            return JsonResponse({"success": False, "message": "Transaction With required"}, status=400)

        invoice = data.get("invoice")
        payment_method = data.get("payment_method")

        bill_amount = data.get("bill_amount") or 0
        discount = data.get("discount") or 0
        net_amount = data.get("net_amount") or 0
        receive = data.get("receive") or 0   # always 0 from frontend
        payment =  0
        due = data.get("due") or 0

        tran_date = data.get("tran_date")

        if tran_date:
            tran_date = datetime.combine(
                datetime.strptime(tran_date, "%Y-%m-%d").date(),
                timezone.localtime().time()
            )
        else:
            tran_date = timezone.localtime()

        products = data.get("products", [])

        # ---- Generate ID ----
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT tran_id 
                FROM transaction__mains
                WHERE tran_id LIKE 'GPA%'
                ORDER BY tran_id DESC
                LIMIT 1
            """)
            row = cursor.fetchone()

            last_number = int(row[0][3:]) if row else 0
            tran_id = "GRE" + str(last_number + 1).zfill(9)

        tran_type = 1   # ✅ GENERAL
        status = 1

        # ---- MAIN TABLE ----
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO transaction__mains
                (tran_id, tran_type, tran_method, tran_user, tran_type_with,
                 store_id, loc_id, tran_date, status, invoice,
                 bill_amount, discount, net_amount, payment, due)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, [
                tran_id, tran_type, payment_method, user_id, tran_type_with,
                store_id, location_id, tran_date, status, invoice,
                bill_amount, discount, net_amount, payment, due
            ])

        # ---- DETAILS ----
        details_data = []

        for row in products:
            details_data.append([
                tran_id,
                tran_type,
                payment_method,
                invoice,
                location_id,
                tran_type_with,
                row[0],   # product id
                1,   # qty
                row[1],
                0,
                0,
                0,
                row[2],   # amount
                row[5],   # total
                0,   # cp
                0,   # mrp
                row[4],   # expiry
                store_id,
                tran_date,
                status,
                discount,
                receive,
                0,
                due
            ])

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

        return JsonResponse({"success": True, "tran_id": tran_id})

    except Exception as e:
        print("🔥 GENERAL PAYMENT ERROR:", e)
        return JsonResponse({"success": False, "error": str(e)}, status=500)
    
def get_transaction_with_users_combo_p(request):

        data = UserInfos.objects.filter(
            tran_user_type__tran_type=1,
            tran_user_type__tran_method='receive'
        ).values(
            'id',
            'user_name',
            'tran_user_type_id'
        ).order_by('user_name')

        return JsonResponse(list(data), safe=False)


