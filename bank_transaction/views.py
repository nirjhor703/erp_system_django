from io import BytesIO
import json
from datetime import datetime

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.db import connection, transaction
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from core.models import UserInfos


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


# =====================================================
# COMMON PRODUCT SEARCH
# Deposit group = 3
# Withdraw group = 4
# =====================================================
def product_search(request):
    q = request.GET.get('q', '').strip()
    offset = int(request.GET.get('offset', 0))
    limit = 10
    mode = request.GET.get('mode', 'deposit')

    group_id = 3 if mode == "deposit" else 4

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
          AND tmh.id = 4
          AND tg.id = %s
          AND t.status = 1
        ORDER BY t.id ASC
        LIMIT %s OFFSET %s
    """

    params = [f"{q}%", group_id, limit, offset]

    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        data = dictfetchall(cursor)

    return JsonResponse({'results': data})


# =====================================================
# DEPOSIT PAGES
# =====================================================
def add_deposit_page(request):
    return render(request, 'bank_transaction/deposit.html')


def deposit_list(request):
    return render(request, 'bank_transaction/deposit_list.html')


def deposit_list_load(request):
    return _bank_list_load(request, prefix="BAD")


def deposit_report_pdf(request):
    return _bank_report_pdf(request, prefix="BAD", title="Deposit Report")


# =====================================================
# WITHDRAW PAGES
# =====================================================
def add_withdraw_page(request):
    return render(request, 'bank_transaction/withdraw.html')


def withdraw_list(request):
    return render(request, 'bank_transaction/withdraw_list.html')


def withdraw_list_load(request):
    return _bank_list_load(request, prefix="BAW")


def withdraw_report_pdf(request):
    return _bank_report_pdf(request, prefix="BAW", title="Withdraw Report")


# =====================================================
# COMMON LIST LOAD
# =====================================================
def _bank_list_load(request, prefix):
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
            m.receive AS receive,
            m.payment AS payment,
            m.due AS due
        FROM transaction__mains m
        WHERE 1=1
    """

    params = []

    if q:
        sql += " AND (m.tran_id LIKE %s OR m.tran_user LIKE %s)"
        params.extend([f"%{q}%", f"%{q}%"])

    sql += " AND m.tran_id LIKE %s"
    params.append(f"{prefix}%")

    if start_date:
        sql += " AND DATE(m.tran_date) >= %s"
        params.append(start_date)

    if end_date:
        sql += " AND DATE(m.tran_date) <= %s"
        params.append(end_date)

    sql += " ORDER BY m.id ASC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        data = dictfetchall(cursor)

    return JsonResponse({'results': data})


# =====================================================
# COMMON PDF REPORT
# =====================================================
def _bank_report_pdf(request, prefix, title):
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
            m.payment,
            m.due
        FROM transaction__mains m
        WHERE 1=1
    """

    params = []

    if q:
        sql += " AND (m.tran_id LIKE %s OR m.tran_user LIKE %s)"
        params.extend([f"%{q}%", f"%{q}%"])

    sql += " AND m.tran_id LIKE %s"
    params.append(f"{prefix}%")

    if start_date:
        sql += " AND DATE(m.tran_date) >= %s"
        params.append(start_date)

    if end_date:
        sql += " AND DATE(m.tran_date) <= %s"
        params.append(end_date)

    sql += " ORDER BY m.id ASC"

    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        data = dictfetchall(cursor)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(title, styles["Title"]))
    elements.append(Spacer(1, 10))

    date_text = f"""
    <b>Start Date:</b> {start_date if start_date else '-'}  
    <b>End Date:</b> {end_date if end_date else '-'}
    """
    elements.append(Paragraph(date_text, styles["Normal"]))
    elements.append(Spacer(1, 20))

    table_data = [
        ["SL", "Tran ID", "Date", "Bank", "User", "Bill", "Disc", "Net", "Receive", "Payment", "Due"]
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
            p["payment"],
            p["due"],
        ])

    table = Table(table_data)

    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return HttpResponse(buffer, content_type="application/pdf")


# =====================================================
# COMBOS
# =====================================================
def get_divisions_combo(request):
    sql = """
        SELECT
            MIN(loc.id) AS id,
            loc.division
        FROM location__infos loc
        GROUP BY loc.division
        ORDER BY loc.division
    """

    with connection.cursor() as cursor:
        cursor.execute(sql)
        data = dictfetchall(cursor)

    return JsonResponse({"divisions_combo": data}, safe=False)


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


# =====================================================
# SAVE DEPOSIT
# payment = deposit
# =====================================================
@csrf_exempt
@transaction.atomic
def save_bank_deposit(request):
    return _save_bank_transaction(
        request=request,
        prefix="BAD",
        receive_value=0,
        payment_from_frontend=True,
        error_name="BANK DEPOSIT ERROR"
    )


# =====================================================
# SAVE WITHDRAW
# receive = withdraw
# =====================================================
@csrf_exempt
@transaction.atomic
def save_bank_withdraw(request):
    return _save_bank_transaction(
        request=request,
        prefix="BAW",
        receive_from_frontend=True,
        payment_value=0,
        error_name="BANK WITHDRAW ERROR"
    )


# =====================================================
# COMMON SAVE FUNCTION
# =====================================================
def _save_bank_transaction(
    request,
    prefix,
    receive_from_frontend=False,
    payment_from_frontend=False,
    receive_value=0,
    payment_value=0,
    error_name="BANK TRANSACTION ERROR"
):
    if request.method != "POST":
        return JsonResponse({"success": False}, status=405)

    try:
        data = json.loads(request.body)

        store_id = data.get("store")
        location_id = data.get("location")
        tran_type_with = data.get("tran_type_with")

        if not tran_type_with:
            return JsonResponse({
                "success": False,
                "message": "Transaction With required"
            }, status=400)

        invoice = data.get("invoice")
        payment_method = data.get("payment_method")

        bill_amount = data.get("bill_amount") or 0
        discount = data.get("discount") or 0
        net_amount = data.get("net_amount") or 0
        due = data.get("due") or 0

        if receive_from_frontend:
            receive = data.get("payment") or data.get("receive") or 0
        else:
            receive = receive_value

        if payment_from_frontend:
            payment = data.get("payment") or 0
        else:
            payment = payment_value

        tran_date = data.get("tran_date")

        if tran_date:
            tran_date = datetime.combine(
                datetime.strptime(tran_date, "%Y-%m-%d").date(),
                timezone.localtime().time()
            )
        else:
            tran_date = timezone.localtime()

        products = data.get("products", [])

        if not products:
            return JsonResponse({
                "success": False,
                "message": "No products selected"
            }, status=400)

        # ---- Generate Transaction ID ----
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT tran_id 
                FROM transaction__mains
                WHERE tran_id LIKE %s
                ORDER BY tran_id DESC
                LIMIT 1
            """, [f"{prefix}%"])

            row = cursor.fetchone()

            last_number = int(row[0][3:]) if row else 0
            tran_id = prefix + str(last_number + 1).zfill(9)

        tran_type = 4
        status = 1
        tran_user = data.get("supplier")

        # ---- MAIN TABLE ----
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO transaction__mains
                (tran_id, tran_type, tran_method, tran_user, tran_type_with,
                 store_id, loc_id, tran_date, status, invoice,
                 bill_amount, discount, net_amount, receive, payment, due)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, [
                tran_id, tran_type, payment_method, tran_user, tran_type_with,
                store_id, location_id, tran_date, status, invoice,
                bill_amount, discount, net_amount, receive, payment, due
            ])

        # ---- DETAILS TABLE ----
        details_data = []

        for row in products:
            product_id = row[0]
            qty = row[1] if len(row) > 1 else 1
            amount = row[2] if len(row) > 2 else 0
            mrp = row[3] if len(row) > 3 else 0
            expiry = row[4] if len(row) > 4 else None
            total = row[5] if len(row) > 5 else amount

            details_data.append([
                tran_id,
                tran_type,
                payment_method,
                invoice,
                location_id,
                tran_type_with,
                product_id,
                1,
                qty,
                0,
                0,
                0,
                amount,
                total,
                0,
                mrp,
                expiry,
                store_id,
                tran_date,
                status,
                discount,
                receive,
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

        return JsonResponse({
            "success": True,
            "tran_id": tran_id
        })

    except Exception as e:
        print(f"🔥 {error_name}:", e)
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)