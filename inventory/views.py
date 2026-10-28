from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from .forms import RegisterForm
from django.db.models import Sum
from .models import Product
from .models import Organization, OrganizationSettings, Product

from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .forms import ProductForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            "Registration successful. Please log in.",
        )
        return redirect("login")

    return render(
        request,
        "registration/register.html",
        {"form": form},
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=email,
            password=password,
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid email or password.")

    return render(request, "registration/login.html")


@login_required
@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, "You have logged out successfully.")
    return redirect("login")



# Dashboard view

@login_required
def dashboard_view(request):
    organization = getattr(request.user, "organization", None)

    if organization is None:
        messages.error(
            request,
            "Your account is not linked to an organization.",
        )
        logout(request)
        return redirect("login")

    products = Product.objects.filter(
        organization=organization
    )

    total_products = products.count()

    total_quantity = products.aggregate(
        total=Sum("quantity")
    )["total"] or 0

    try:
        default_threshold = (
            organization.settings.default_low_stock_threshold
        )
    except OrganizationSettings.DoesNotExist:
        default_threshold = 5

    '''low_stock_products = [
        product
        for product in products
        if product.quantity <= (
            product.low_stock_threshold
            if product.low_stock_threshold is not None
            else default_threshold
        )
    ]'''
    
    low_stock_products = []

    for product in products:
        effective_threshold = (
            product.low_stock_threshold
            if product.low_stock_threshold is not None
            else default_threshold
        )

        if product.quantity <= effective_threshold:
            product.effective_low_stock_threshold = effective_threshold
            low_stock_products.append(product)


    context = {
        "organization": organization,
        "total_products": total_products,
        "total_quantity": total_quantity,
        "low_stock_products": low_stock_products,
    }

    return render(
        request,
        "inventory/dashboard.html",
        context,
    )





@login_required
def product_list_view(request):
    organization = get_object_or_404(
        Organization,
        user=request.user
    )

    products = Product.objects.filter(
        organization=organization
    )

    search_query = request.GET.get("q", "").strip()

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
            | Q(sku__icontains=search_query)
        )

    try:
        default_threshold = (
            organization.settings.default_low_stock_threshold
        )
    except OrganizationSettings.DoesNotExist:
        default_threshold = 5

    for product in products:
        if product.low_stock_threshold is not None:
            effective_threshold = product.low_stock_threshold
        else:
            effective_threshold = default_threshold

        product.is_low_stock = (
            product.quantity <= effective_threshold
        )
        product.effective_low_stock_threshold = effective_threshold

    context = {
        "products": products,
        "search_query": search_query,
    }

    return render(
        request,
        "inventory/product_list.html",
        context
    )



@login_required
def product_create_view(request):
    organization = get_object_or_404(
        Organization,
        user=request.user,
    )

    if request.method == "POST":
        form = ProductForm(
            request.POST,
            organization=organization,
        )

        if form.is_valid():
            try:
                with transaction.atomic():
                    product = form.save(commit=False)
                    product.organization = organization
                    product.save()

                messages.success(
                    request,
                    "Product created successfully.",
                )
                return redirect("product_list")

            except IntegrityError:
                form.add_error(
                    "sku",
                    "This SKU already exists in your organization.",
                )
    else:
        form = ProductForm(organization=organization)

    return render(
        request,
        "inventory/product_form.html",
        {
            "form": form,
            "page_title": "Add Product",
            "button_text": "Create Product",
        },
    )




@login_required
def product_edit_view(request, pk):
    organization = get_object_or_404(
        Organization,
        user=request.user,
    )

    product = get_object_or_404(
        Product,
        pk=pk,
        organization=organization,
    )

    if request.method == "POST":
        form = ProductForm(
            request.POST,
            instance=product,
            organization=organization,
        )

        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()

                messages.success(
                    request,
                    "Product updated successfully.",
                )
                return redirect("product_list")

            except IntegrityError:
                form.add_error(
                    "sku",
                    "This SKU already exists in your organization.",
                )
    else:
        form = ProductForm(
            instance=product,
            organization=organization,
        )

    return render(
        request,
        "inventory/product_form.html",
        {
            "form": form,
            "page_title": "Edit Product",
            "button_text": "Save Changes",
        },
    )



@login_required
def product_delete_view(request, pk):
    organization = get_object_or_404(
        Organization,
        user=request.user,
    )

    product = get_object_or_404(
        Product,
        pk=pk,
        organization=organization,
    )

    if request.method == "POST":
        product.delete()

        messages.success(
            request,
            "Product deleted successfully.",
        )
        return redirect("product_list")

    return render(
        request,
        "inventory/product_confirm_delete.html",
        {"product": product},
    )
