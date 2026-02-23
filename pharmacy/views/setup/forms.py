from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from pharmacy.models import ItemForms, CompanyDetails, TransactionMainHeads

def form_list(request):
    rows_per_page = request.GET.get('rows', 15)
    try:
        rows_per_page = int(rows_per_page)
    except:
        rows_per_page = 15

    # Use session variable, not module_id directly
    active_module = request.session.get('active_module')

    forms = ItemForms.objects.select_related('company', 'type')\
        .filter(status=1, type_id=active_module)\
        .order_by('added_at')  # oldest first

    companies = CompanyDetails.objects.filter(status=1).order_by('company_name')
    types = TransactionMainHeads.objects.filter(status=1).order_by('type_name')

    paginator = Paginator(forms, rows_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'pharmacy/setup/form_list.html', {
        'forms': page_obj,
        'companies': companies,
        'types': types,
        'rows_per_page': rows_per_page,
        'rows_options': [15,30,50,100,500]
    })




def add_form(request):
    if request.method == "POST":
        name = request.POST.get('form_name')
        company_id = request.POST.get('company')
        type_id = request.POST.get('type')

        if not name or not company_id:
            return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

        company = CompanyDetails.objects.get(company_id=company_id)
        type_obj = TransactionMainHeads.objects.get(id=type_id) if type_id else None

        # Create the new form
        ItemForms.objects.create(
            form_name=name,
            company=company,
            type=type_obj,
            status=1,
            added_at=timezone.now()
        )

        # 🔹 Compute last page after addition
        active_module = request.session.get('active_module')
        forms = ItemForms.objects.filter(status=1, type_id=active_module).order_by('added_at')
        paginator = Paginator(forms, 15)  # or use rows_per_page if dynamic
        last_page = paginator.num_pages

        return JsonResponse({'status': 'success', 'last_page': last_page})


def get_form(request, id):
    f = get_object_or_404(ItemForms, id=id)
    return JsonResponse({
        'id': f.id,
        'form_name': f.form_name,
        'company': f.company.company_id if f.company else None,
        'type': f.type.id if f.type else None
    })


def update_form(request):
    if request.method == "POST":
        f = ItemForms.objects.get(id=request.POST.get('id'))
        f.form_name = request.POST.get('form_name')

        company_id = request.POST.get('company')
        if company_id:
            f.company = CompanyDetails.objects.get(company_id=company_id)

        type_id = request.POST.get('type')
        if type_id:
            f.type = TransactionMainHeads.objects.get(id=type_id)

        f.updated_at = timezone.now()
        f.save()
        return JsonResponse({'status':'updated'})


def delete_form(request, id):
    ItemForms.objects.filter(id=id).delete()
    return JsonResponse({'status':'deleted'})
