from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from pharmacy.models import TransactionHeads, TransactionGroupes, ItemCategories, ItemForms, ItemManufacturers, ItemUnits, CompanyDetails
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.utils import timezone

# ================= LIST PHARMACY PRODUCTS =================
def pharmacy_products_list(request):
    rows_per_page = int(request.GET.get("rows", 15))
    page = request.GET.get("page", 1)
    module_id = request.session.get('active_module')
    print("Active module:", module_id)
    products = TransactionHeads.objects.select_related(
        'groupe', 'category', 'manufacturer', 'form', 'unit', 'company'
    ).filter(
        status=1,
        groupe__tran_groupe_type_id=module_id
    ).order_by('id')
    print("products count:", products.count())  # Debug

    paginator = Paginator(products, rows_per_page)

    if page == 'last':
        page = paginator.num_pages
    page = int(page)

    products_page = paginator.get_page(page)

    context = {
        'products': products_page,
        'rows_per_page': rows_per_page,
        'groupes': TransactionGroupes.objects.filter(
            status=1,
            tran_groupe_type_id=module_id
        ),
        'categories': ItemCategories.objects.filter(
            status=1,
            type_id=module_id
        ),
        'manufacturers': ItemManufacturers.objects.filter(status=1),
        'forms': ItemForms.objects.filter(status=1),
        'units': ItemUnits.objects.filter(status=1),
        'companies': CompanyDetails.objects.filter(status=1),
        'module_id': module_id
    }

    return render(request, 'pharmacy/setup/pharmacy_products.html', context)


# ================= ADD PRODUCT =================
@csrf_exempt
def pharmacy_product_add(request):
    if request.method == "POST":
        product_name = request.POST.get("product_name")
        groupe_id = request.POST.get("groupe")
        category_id = request.POST.get("category") or None
        manufacturer_id = request.POST.get("manufacturer") or None
        form_id = request.POST.get("form") or None
        unit_id = request.POST.get("unit") or None
        company_id = request.POST.get("company")

        product = TransactionHeads.objects.create(
            tran_head_name=product_name,
            groupe_id=groupe_id,
            category_id=category_id,
            manufacturer_id=manufacturer_id,
            form_id=form_id,
            unit_id=unit_id,
            quantity=0,
            cp=0,
            mrp=0,
            company_id=company_id,
            status=1,
            editable=1,
            added_at=timezone.now(),
            updated_at=timezone.now()
        )
        rows_per_page = 15
        products = TransactionHeads.objects.all().order_by('id')
        paginator = Paginator(products, rows_per_page)  # <-- positional only
        last_page = paginator.num_pages

        return JsonResponse({'id': product.id, 'last_page': last_page})

# ================= EDIT PRODUCT =================
@csrf_exempt
def pharmacy_product_edit(request, id):
    if request.method == "POST":
        product = get_object_or_404(TransactionHeads, pk=id)
        product.tran_head_name = request.POST.get("product_name")
        product.groupe_id = request.POST.get("groupe")
        product.category_id = request.POST.get("category") or None
        product.manufacturer_id = request.POST.get("manufacturer") or None
        product.form_id = request.POST.get("form") or None
        product.unit_id = request.POST.get("unit") or None
        product.company_id = request.POST.get("company")
        product.updated_at = timezone.now()
        product.save()
        return JsonResponse({'success': True})

# ================= DELETE PRODUCT =================
@csrf_exempt
def pharmacy_product_delete(request, id):
    if request.method == "POST":
        product = get_object_or_404(TransactionHeads, pk=id)
        product.delete()
        return JsonResponse({'success': True})
