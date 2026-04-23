from django.shortcuts import render
from django.utils import timezone
from django.http import JsonResponse
from .models import TransactionWiths
from main_heads.models import TransactionMainHeads


def transaction_with_page(request):
    transaction_withs = TransactionWiths.objects.filter(status=1).order_by('id')
    heads = TransactionMainHeads.objects.filter(status=1).order_by('id')
    method_choices = ['Receive', 'Payment', 'Both']

    return render(request, 'transaction_with/transaction_with.html', {
        'transaction_withs': transaction_withs,
        'heads': heads,
        'method_choices': method_choices,
    })


def transaction_with_store(request):
    if request.method == 'POST':
        TransactionWiths.objects.create(
            tran_with_name=request.POST['tran_with_name'],
            tran_type=request.POST['tran_type'],
            user_role=0,
            tran_method=request.POST['tran_method'],
            status=1,
            added_at=timezone.now()
        )
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'message': 'Invalid request'})


def transaction_with_fetch(request):
    try:
        t = TransactionWiths.objects.get(id=request.GET['id'])
        return JsonResponse({
            'id': t.id,
            'tran_with_name': t.tran_with_name,
            'tran_type': t.tran_type,
            'tran_method': t.tran_method,
        })
    except TransactionWiths.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Data not found'})


def transaction_with_update(request):
    if request.method == 'POST':
        try:
            t = TransactionWiths.objects.get(id=request.POST['id'])
            t.tran_with_name = request.POST['tran_with_name']
            t.tran_type = request.POST['tran_type']
            t.tran_method = request.POST['tran_method']
            t.updated_at = timezone.now()
            t.save()

            return JsonResponse({'success': True})
        except TransactionWiths.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Data not found'})

    return JsonResponse({'success': False, 'message': 'Invalid request'})


def transaction_with_delete(request):
    if request.method == 'POST':
        TransactionWiths.objects.filter(id=request.POST['id']).update(
            status=0,
            updated_at=timezone.now()
        )
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'message': 'Invalid request'})