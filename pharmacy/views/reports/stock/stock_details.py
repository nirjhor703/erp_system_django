from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from pharmacy.models import TransactionDetails, TransactionHeads

# Helper to get tran_type from URL segment
def get_tran_type(segment):
    try:
        return int(segment)
    except:
        return 0

# Show all stock details
def show_stock_details(request):
    tran_type = get_tran_type(request.path.strip('/').split('/')[-1])
    
    data = TransactionDetails.objects.filter(
        tran_method__in=['Purchase', 'Positive'],
        tran_type=tran_type,
        quantity__gt=0
    ).select_related('store')

    serialized = [
        {
            "tran_id": d.tran_id,
            "tran_method": d.tran_method,
            "quantity_actual": d.quantity_actual,
            "tran_date": d.tran_date,
        }
        for d in data
    ]

    return render(request, 'pharmacy/reports/stock/stock_details.html', {'data': serialized, 'name': 'Stock Details', 'js': 'stock_details'})

# Search stock details
def search_stock_details(request):
    tran_type = get_tran_type(request.path.strip('/').split('/')[-2])
    search = request.GET.get('search', '')
    search_option = int(request.GET.get('searchOption', 1))

    # Base queryset
    heads = TransactionHeads.objects.all()

    # Filtering based on searchOption
    if search:
        if search_option == 1:
            heads = heads.filter(tran_head_name__istartswith=search)
        elif search_option == 2:
            heads = heads.filter(category__category_name__istartswith=search)
        elif search_option == 3:
            heads = heads.filter(manufacturer__manufacturer_name__istartswith=search)
        elif search_option == 4:
            heads = heads.filter(form__form_name__istartswith=search)
        elif search_option == 6:
            heads = heads.filter(store__store_name__istartswith=search)

    head_ids = heads.values_list('id', flat=True)

    data = TransactionDetails.objects.filter(
        tran_method__in=['Purchase', 'Positive'],
        tran_type=tran_type,
        quantity__gt=0,
        tran_head_id__in=head_ids
    ).select_related('store')

    serialized = [
        {
            "tran_id": d.tran_id,
            "tran_method": d.tran_method,
            "quantity_actual": d.quantity_actual,
            "tran_date": d.tran_date,
        }
        for d in data
    ]

    return JsonResponse({"status": True, "data": serialized})

# Print PDF
def print_stock_details(request):
    tran_type = get_tran_type(request.path.strip('/').split('/')[-1])
    start_date = request.GET.get('startDate', datetime.today().strftime('%Y-%m-%d'))
    end_date = request.GET.get('endDate', datetime.today().strftime('%Y-%m-%d'))

    data = TransactionDetails.objects.filter(
        tran_method__in=['Purchase', 'Positive'],
        tran_type=tran_type,
        quantity__gt=0
    ).select_related('store').order_by('id')

    # Create PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="stock_details_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph("Stock Details Report", styles['Title']))
    elements.append(Paragraph(f"As on: {start_date} - {end_date}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Table header
    table_data = [
        ["SL", "Status", "Receive", "Issue", "Supplier Return", "Client Return", "Balance", "Tran Id", "Date"]
    ]

    balance = 0
    for i, d in enumerate(data, start=1):
        if d.tran_method in ["Purchase", "Positive"]:
            balance += d.quantity_actual
        elif d.tran_method in ["Issue", "Negative"]:
            balance -= d.quantity_actual
        elif d.tran_method == "Supplier Return":
            balance -= d.quantity_actual
        elif d.tran_method == "Client Return":
            balance += d.quantity_actual

        table_data.append([
            i,
            d.tran_method,
            d.quantity_actual if d.tran_method in ["Purchase", "Positive"] else 0,
            d.quantity_actual if d.tran_method in ["Issue", "Negative"] else 0,
            d.quantity_actual if d.tran_method == "Supplier Return" else 0,
            d.quantity_actual if d.tran_method == "Client Return" else 0,
            balance,
            d.tran_id,
            d.tran_date.strftime("%d-%m-%Y")
        ])

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('ALIGN', (2,1), (-2,-1), 'RIGHT'),
        ('ALIGN', (-2,1), (-1,-1), 'CENTER')
    ]))

    elements.append(table)
    doc.build(elements)
    return response