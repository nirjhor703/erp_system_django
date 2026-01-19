from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from django.http import JsonResponse
from .models import TransactionGroupes, TransactionMainHeads, CompanyDetails

def transaction_groupe_page(request):
    groupes = TransactionGroupes.objects.filter(status=1).order_by('id')
    heads = TransactionMainHeads.objects.filter(status=1)
    companies = CompanyDetails.objects.filter(status=1)
    methods = TransactionGroupes.objects.values_list('tran_method', flat=True).distinct()
    return render(request, 'transaction_groupes/transaction_groups.html', {
        'groupes': groupes,
        'heads': heads,
        'companies': companies,
        "methods": methods
    })


def transaction_groupe_store(request):
    TransactionGroupes.objects.create(
        tran_groupe_name=request.POST['tran_groupe_name'],
        tran_groupe_type_id=request.POST['tran_groupe_type'],
        tran_method=request.POST['tran_method'],
        company_id=request.POST.get('company'),
        status=1,
        added_at=timezone.now()
    )
    return JsonResponse({'success': True})


def transaction_groupe_fetch(request):
    g = TransactionGroupes.objects.get(id=request.GET['id'])
    return JsonResponse({
        'id': g.id,
        'tran_groupe_name': g.tran_groupe_name,
        'tran_groupe_type': g.tran_groupe_type_id,
        'tran_method': g.tran_method,
        'company': g.company_id
    })


def transaction_groupe_update(request):
    g = TransactionGroupes.objects.get(id=request.POST['id'])
    g.tran_groupe_name = request.POST['tran_groupe_name']
    g.tran_groupe_type_id = request.POST['tran_groupe_type']
    g.tran_method = request.POST['tran_method']
    g.company_id = request.POST.get('company')
    g.updated_at = timezone.now()
    g.save()
    return JsonResponse({'success': True})


def transaction_groupe_delete(request):
    TransactionGroupes.objects.filter(id=request.POST['id']).update(status=0)
    return JsonResponse({'success': True})
