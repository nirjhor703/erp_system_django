from django.shortcuts import redirect, render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from pharmacy.models import ItemCategories, CompanyDetails, TransactionMainHeads, TransactionGroupes

def category_list(request):
    rows_per_page = int(request.GET.get('rows', 15))
    search = request.GET.get('search', '').strip()

    module_id = request.session.get('active_module')

    # Safety check
    if not module_id:
        return redirect('dashboard')  # or wherever module is selected

    selected_type = get_object_or_404(TransactionMainHeads, id=module_id)

    categories = ItemCategories.objects.select_related('company', 'type', 'group')\
        .filter(status=1, type_id=module_id)

    if search:
        categories = categories.filter(category_name__icontains=search)

    categories = categories.order_by('added_at')

    companies = CompanyDetails.objects.filter(status=1).order_by('company_name')
    types = TransactionMainHeads.objects.filter(status=1).order_by('type_name')


    paginator = Paginator(categories, rows_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'pharmacy/setup/category_list.html', {
        'categories': page_obj,
        'companies': companies,
        'types': types,
        'selected_type': selected_type,  # 👈 only this
        'module_id': module_id,          # 👈 needed for JS
        'rows_per_page': rows_per_page,
        'search': search
    })


def get_groups_by_type(request):
    type_id = request.GET.get('type_id')
    if not type_id:
        return JsonResponse({'groups': []})

    groups = TransactionGroupes.objects.filter(
        status=1,
        tran_groupe_type_id=type_id
    ).order_by('tran_groupe_name')

    data = [{'id': g.id, 'name': g.tran_groupe_name} for g in groups]
    return JsonResponse({'groups': data})

def add_category(request):
    if request.method == "POST":
        name = request.POST.get('category_name')
        company_id = request.POST.get('company')

        if not name or not company_id:
            return JsonResponse({'status': 'error', 'message': 'Missing fields'})

        company = get_object_or_404(CompanyDetails, company_id=company_id)

        module_id = request.session.get('active_module')  # 🆕 ADD THIS LINE – assign to current module
        type_id = request.POST.get('type')
        type_obj = get_object_or_404(TransactionMainHeads, id=type_id)

        group_id = request.POST.get('group')
        group = None
        if group_id:
            group = TransactionGroupes.objects.filter(id=group_id).first()



        ItemCategories.objects.create(
            category_name=name,
            company=company,
            type=type_obj,
            group=group,
            status=1,
            added_at=timezone.now()
        )

        total = ItemCategories.objects.filter(status=1, type_id=module_id).count()  # 🆕 filter by module
        last_page = (total // 15) + (1 if total % 15 else 0)

        return JsonResponse({'status': 'success', 'last_page': last_page})


def get_category(request, id):
    c = get_object_or_404(ItemCategories, id=id)
    return JsonResponse({
        'id': c.id,
        'category_name': c.category_name,
        'company': c.company.company_id if c.company else '',
        'type': c.type.id if c.type else '',
        'group': c.group.id if c.group else ''

    })




def update_category(request):
    if request.method == "POST":
        c = get_object_or_404(ItemCategories, id=request.POST.get('id'))

        c.category_name = request.POST.get('category_name')

        company_id = request.POST.get('company')
        c.company = CompanyDetails.objects.filter(company_id=company_id).first()

        type_id = request.POST.get('type')
        c.type = TransactionMainHeads.objects.filter(id=type_id).first()


        group_id = request.POST.get('group')
        if group_id:
            c.group = TransactionGroupes.objects.filter(id=group_id).first()
        else:
            c.group = None



        c.updated_at = timezone.now()
        c.save()

        return JsonResponse({'status': 'updated'})


def delete_category(request, id):
    ItemCategories.objects.filter(id=id).update(status=0)
    return JsonResponse({'status': 'deleted'})