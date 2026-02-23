from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from pharmacy.models import TransactionGroupes, TransactionMainHeads, CompanyDetails
from django.core.paginator import Paginator

def transaction_groupe_list(request):
    rows = int(request.GET.get('rows', 15))
    module_id = request.session.get('active_module')
    print("Active module:", module_id)
    groupes = TransactionGroupes.objects.select_related('company')\
                    .filter(status=1, tran_groupe_type=module_id)\
                    .order_by('id')
    print("tran_group count:", groupes.count())  # Debug
    paginator = Paginator(groupes, rows)
    page_number = request.GET.get('page')

    # If user sends 'last' as page
    if page_number == 'last':
        page_number = paginator.num_pages

    groupes_page = paginator.get_page(page_number)

    context = {
        'groupes': groupes_page,
        'rows_per_page': rows,
        'companies': CompanyDetails.objects.filter(status=1),
        'module_id': module_id
    }
    return render(request, 'pharmacy/setup/transaction_groupes.html', context)


def add_transaction_groupe(request):
    if request.method == 'POST':
        g = TransactionGroupes.objects.create(
            tran_groupe_name=request.POST.get('tran_groupe_name'),
            company_id=request.POST.get('company'),
            tran_groupe_type_id=1,  # default type
            tran_method='Manual',    # default method
            status=1,
            added_at=timezone.now()
        )
        return JsonResponse({'success': True, 'id': g.id})


def get_transaction_groupe(request):
    g = get_object_or_404(TransactionGroupes, id=request.GET.get('id'))
    data = {
        'id': g.id,
        'tran_groupe_name': g.tran_groupe_name,
        'tran_groupe_type': g.tran_groupe_type_id,
        'tran_method': g.tran_method,
        'company': g.company.company_id if g.company else '',
    }
    return JsonResponse(data)


def update_transaction_groupe(request):
    if request.method == 'POST':
        g = TransactionGroupes.objects.get(id=request.POST.get('id'))
        g.tran_groupe_name = request.POST.get('tran_groupe_name')
        g.company_id = request.POST.get('company')
        g.updated_at = timezone.now()
        g.save()
        return JsonResponse({'success': True})



def delete_transaction_groupe(request):
    if request.method == 'POST':
        TransactionGroupes.objects.filter(id=request.POST.get('id')).delete()
        return JsonResponse({'success': True})

