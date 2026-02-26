from django.shortcuts import render
from pharmacy.models import TransactionDetails
from django.utils import timezone

def item_flow_report(request):
    start_date = request.GET.get('startDate') or timezone.now().date()
    end_date = request.GET.get('endDate') or timezone.now().date()
    search_value = request.GET.get('search', '')

    # Filter transactions
    data = TransactionDetails.objects.filter(tran_date__date__range=[start_date, end_date])
    if search_value:
        data = data.filter(tran_id__icontains=search_value)

    # Calculate balance cumulatively
    balance = 0
    data_with_balance = []
    opening_balance = 0  # or fetch from your opening balance logic
    balance = opening_balance

    for item in data.order_by('tran_date', 'id'):
        if item.tran_method in ["Purchase", "Positive", "Client Return"]:
            balance += item.quantity_actual
        elif item.tran_method in ["Issue", "Negative", "Supplier Return"]:
            balance -= item.quantity_actual

        data_with_balance.append({
            'tran_id': item.tran_id,
            'tran_method': item.tran_method,
            'quantity_actual': item.quantity_actual,
            'tran_date': item.tran_date,
            'balance': balance
        })

    context = {
        'report_name': "Item Flow Report",
        'start_date': start_date,
        'end_date': end_date,
        'data': data_with_balance,
        'opening_balance': opening_balance,
        'user': request.user,
    }

    return render(request, 'pharmacy/reports/item_flow.html', context)