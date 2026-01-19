from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from pharmacy.models import ItemManufacturers, CompanyDetails, TransactionMainHeads
from django.core.paginator import Paginator

def manufacturer_list(request):
    # Rows per page
    rows_per_page = request.GET.get('rows', 15)
    try:
        rows_per_page = int(rows_per_page)
    except:
        rows_per_page = 15

    # 🆕 Get active module from session
    module_id = request.session.get('active_module')
    print("Active module:", module_id)  

    # 🆕 Filter by module_id (type)
    manufacturers = ItemManufacturers.objects.select_related('company', 'type')\
                    .filter(status=1, type_id=module_id).order_by('added_at')
    print("Manufacturers count:", manufacturers.count())
    companies = CompanyDetails.objects.filter(status=1).order_by('company_name')
    types = TransactionMainHeads.objects.filter(status=1).order_by('type_name')

    paginator = Paginator(manufacturers, rows_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'pharmacy/setup/manufacturer_list.html', {
        'manufacturers': page_obj,
        'companies': companies,
        'types': types,
        'rows_per_page': rows_per_page,
        'module_id': module_id,  # 🆕 for debug / template use if needed
        
    })


def add_manufacturer(request):
    if request.method == "POST":
        name = request.POST.get('manufacturer_name')
        company_id = request.POST.get('company')

        module_id = request.session.get('active_module')  # 🆕 Assign module id

        if name and company_id and module_id:
            company = get_object_or_404(CompanyDetails, company_id=company_id)
            type_obj = get_object_or_404(TransactionMainHeads, id=module_id)

            ItemManufacturers.objects.create(
                manufacturer_name=name,
                company=company,
                type=type_obj,  # 🆕 assign module/type
                status=1,
                added_at=timezone.now()
            )
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Missing required fields or module not set'})


def get_manufacturer(request, id):
    m = get_object_or_404(ItemManufacturers, id=id)
    return JsonResponse({
        'id': m.id,
        'manufacturer_name': m.manufacturer_name,
        'company': m.company.company_id if m.company else '',
        'type': m.type.id if m.type else ''
    })


def update_manufacturer(request):
    if request.method == "POST":
        m = get_object_or_404(ItemManufacturers, id=request.POST.get('id'))
        company_id = request.POST.get('company')
        module_id = request.session.get('active_module')

        m.manufacturer_name = request.POST.get('manufacturer_name')
        m.company = get_object_or_404(CompanyDetails, company_id=company_id)
        m.type = get_object_or_404(TransactionMainHeads, id=module_id)  # 🆕 force module
        m.save()

        return JsonResponse({'status': 'updated'})

    return JsonResponse({'status': 'error'})


def delete_manufacturer(request, id):
    ItemManufacturers.objects.filter(id=id).delete()
    return JsonResponse({'status': 'deleted'})