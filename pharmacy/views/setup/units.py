from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from pharmacy.models import ItemUnits, CompanyDetails, TransactionMainHeads
from django.core.paginator import Paginator


def unit_list(request):
    # 🔹 Rows per page
    rows_per_page = request.GET.get('rows', 15)
    try:
        rows_per_page = int(rows_per_page)
    except:
        rows_per_page = 15

    # 🔹 Active module id from session
    module_id = request.session.get('active_module')
    print("Active module:", module_id)  

    # 🔹 Fetch units filtered by module
    units = ItemUnits.objects.select_related('company', 'type')\
            .filter(status=1, type_id=module_id).order_by('added_at')
    print("Units count:", units.count())

    companies = CompanyDetails.objects.filter(status=1).order_by('company_name')
    types = TransactionMainHeads.objects.filter(status=1).order_by('type_name')

    paginator = Paginator(units, rows_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    rows_options = [15, 30, 50, 100, 500]  # add this

    return render(request, 'pharmacy/setup/unit_list.html', {
        'units': page_obj,
        'companies': companies,
        'rows_per_page': rows_per_page,
        'rows_options': rows_options,  # pass it to template
    })



def add_unit(request):
    if request.method == "POST":
        name = request.POST.get('unit_name')
        company_id = request.POST.get('company')
        module_id = request.session.get('active_module')  # active module id
        rows_per_page = request.POST.get('rows', 15)      # get current rows per page

        try:
            rows_per_page = int(rows_per_page)
        except:
            rows_per_page = 15

        if name and company_id and module_id:
            company = get_object_or_404(CompanyDetails, company_id=company_id)
            type_obj = get_object_or_404(TransactionMainHeads, id=module_id)

            # 1️⃣ Create new unit
            ItemUnits.objects.create(
                unit_name=name,
                company=company,
                type=type_obj,
                status=1,
                added_at=timezone.now()
            )

            # 2️⃣ Get all units for this module and calculate last page
            units = ItemUnits.objects.filter(status=1, type_id=module_id).order_by('added_at')  # oldest first
            paginator = Paginator(units, rows_per_page)
            last_page = paginator.num_pages

            # 3️⃣ Return success with last page info
            return JsonResponse({'status':'success', 'last_page': last_page})
        else:
            return JsonResponse({'status':'error', 'message':'Missing required fields or module not set'})


def get_unit(request, id):
    u = get_object_or_404(ItemUnits, id=id)
    return JsonResponse({
        'id': u.id,
        'unit_name': u.unit_name,
        'company': u.company.company_id if u.company else '',
        'type': u.type.id if u.type else ''
    })


def update_unit(request):
    if request.method == "POST":
        u = get_object_or_404(ItemUnits, id=request.POST.get('id'))
        company_id = request.POST.get('company')
        module_id = request.session.get('active_module')

        u.unit_name = request.POST.get('unit_name')
        u.company = get_object_or_404(CompanyDetails, company_id=company_id)
        u.type = get_object_or_404(TransactionMainHeads, id=module_id)
        u.updated_at = timezone.now()
        u.save()

        return JsonResponse({'status': 'updated'})

    return JsonResponse({'status': 'error'})


def delete_unit(request, id):
    ItemUnits.objects.filter(id=id).delete()
    return JsonResponse({'status': 'deleted'})
