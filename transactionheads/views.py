from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

from core.models import *

def transaction_heads(request):

    search = request.GET.get('search')
    rows = int(request.GET.get('rows', 15))   # 🔥 NEW

    qs = TransactionHeads.objects.select_related(
        'groupe', 'category', 'manufacturer', 'form', 'unit', 'company'
    ).order_by('id')

    if search:
        qs = qs.filter(
            Q(tran_head_name__icontains=search) |
            Q(groupe__tran_groupe_name__icontains=search) |
            Q(category__category_name__icontains=search) |
            Q(manufacturer__manufacturer_name__icontains=search) |
            Q(form__form_name__icontains=search) |
            Q(unit__unit_name__icontains=search) |
            Q(company__company_name__icontains=search)
        )

    paginator = Paginator(qs, rows)   # 🔥 FIXED
    page = request.GET.get('page')

    if page == 'last':
        page_number = paginator.num_pages
    else:
        page_number = page

    page_obj = paginator.get_page(page_number)

    context = {
        'heads': page_obj,
        'groups': TransactionGroupes.objects.all(),
        'categories': ItemCategories.objects.all(),
        'manufacturers': ItemManufacturers.objects.all(),
        'forms': ItemForms.objects.all(),
        'units': ItemUnits.objects.all(),
        'companies': CompanyDetails.objects.all(),
        'page_obj': page_obj,
        'rows_per_page': rows,   # 🔥 PASS TO TEMPLATE
    }

    return render(request, 'transaction_heads/transaction_heads.html', context)


def transaction_head_add(request):
    if request.method == "POST":
        obj = TransactionHeads.objects.create(
            tran_head_name=request.POST.get('tran_head_name'),
            groupe_id=request.POST.get('groupe'),
            category_id=request.POST.get('category') or None,
            manufacturer_id=request.POST.get('manufacturer') or None,
            form_id=request.POST.get('form') or None,
            unit_id=request.POST.get('unit'),
            quantity=request.POST.get('quantity') or 0,
            cp=request.POST.get('cp') or 0,
            mrp=request.POST.get('mrp') or 0,
            expiry_date=request.POST.get('expiry_date') or None,
            editable=1,
            company_id=request.POST.get('company') or None,
            status=1,
            added_at=timezone.now()
        )
        return JsonResponse({'status': 'success', 'id': obj.id})


def transaction_head_edit(request, id):
    obj = get_object_or_404(TransactionHeads, id=id)

    # ---------- GET (LOAD DATA) ----------
    if request.method == "GET":
        return JsonResponse({
            "id": obj.id,
            "tran_head_name": obj.tran_head_name,
            "groupe_id": obj.groupe_id,
            "category_id": obj.category_id,
            "manufacturer_id": obj.manufacturer_id,
            "form_id": obj.form_id,
            "unit_id": obj.unit_id,
            "mrp": obj.mrp,
            "company_id": obj.company_id,
            "editable": obj.editable,
        })

    # ---------- POST (UPDATE) ----------
    if request.method == "POST":
        obj.tran_head_name = request.POST.get('tran_head_name')
        obj.groupe_id = request.POST.get('groupe')
        obj.category_id = request.POST.get('category') or None
        obj.manufacturer_id = request.POST.get('manufacturer') or None
        obj.form_id = request.POST.get('form') or None
        obj.unit_id = request.POST.get('unit')
        obj.mrp = request.POST.get('mrp') or 0
        obj.editable = 1 if request.POST.get('editable') else 0
        obj.updated_at = timezone.now()
        obj.save()

        return JsonResponse({'status': 'success'})



def transaction_head_delete(request, id):
    TransactionHeads.objects.filter(id=id).delete()
    return JsonResponse({'status': 'success'})
