from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.views.decorators.http import require_POST

from .cart import (
    build_cart_items,
    clear_cart,
    get_cart,
    save_cart,
)
from .forms import (
    CheckoutForm,
    RegisterForm,
)
from .models import (
    Category,
    Order,
    OrderItem,
    Product,
)


def product_list(request):
    products = (
        Product.objects
        .filter(is_active=True)
        .select_related("category")
    )

    categories = Category.objects.all()

    category_slug = request.GET.get(
        "category",
        "",
    )

    query = request.GET.get(
        "q",
        "",
    ).strip()

    if category_slug:
        products = products.filter(
            category__slug=category_slug,
        )

    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
        )

    return render(
        request,
        "shop/product_list.html",
        {
            "products": products,
            "categories": categories,
            "selected_category": category_slug,
            "query": query,
        },
    )


def product_detail(
    request,
    slug,
):
    product = get_object_or_404(
        Product.objects.select_related(
            "category",
        ),
        slug=slug,
        is_active=True,
    )

    return render(
        request,
        "shop/product_detail.html",
        {
            "product": product,
        },
    )


def register(request):
    if request.user.is_authenticated:
        return redirect(
            "shop:product-list",
        )

    if request.method == "POST":
        form = RegisterForm(
            request.POST,
        )

        if form.is_valid():
            user = form.save()
            login(request, user)

            return redirect(
                "shop:product-list",
            )
    else:
        form = RegisterForm()

    return render(
        request,
        "register.html",
        {
            "form": form,
        },
    )


def cart_detail(request):
    items, total = build_cart_items(
        request,
    )

    return render(
        request,
        "shop/cart.html",
        {
            "items": items,
            "total": total,
        },
    )


@require_POST
def cart_add(
    request,
    product_id,
):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
    )

    try:
        quantity = int(
            request.POST.get(
                "quantity",
                1,
            )
        )
    except ValueError:
        quantity = 1

    quantity = max(
        1,
        quantity,
    )

    cart = get_cart(request)
    current_quantity = int(
        cart.get(
            str(product.id),
            0,
        )
    )

    new_quantity = current_quantity + quantity

    if new_quantity > product.stock:
        messages.error(
            request,
            "Omborda buncha mahsulot mavjud emas.",
        )

        return redirect(
            product.get_absolute_url(),
        )

    cart[str(product.id)] = new_quantity
    save_cart(request, cart)

    messages.success(
        request,
        "Mahsulot savatga qo‘shildi.",
    )

    return redirect(
        "shop:cart",
    )


@require_POST
def cart_remove(
    request,
    product_id,
):
    cart = get_cart(request)

    cart.pop(
        str(product_id),
        None,
    )

    save_cart(request, cart)

    return redirect(
        "shop:cart",
    )


@login_required
def checkout(request):
    items, total = build_cart_items(
        request,
    )

    if not items:
        messages.error(
            request,
            "Savat bo‘sh.",
        )

        return redirect(
            "shop:product-list",
        )

    if request.method == "POST":
        form = CheckoutForm(
            request.POST,
        )

        if form.is_valid():
            try:
                with transaction.atomic():
                    order = form.save(
                        commit=False,
                    )

                    order.user = request.user
                    order.total_price = Decimal(
                        "0.00"
                    )

                    order.save()

                    final_total = Decimal(
                        "0.00"
                    )

                    for item in items:
                        product_id = item[
                            "product"
                        ].id

                        try:
                            product = (
                                Product.objects
                                .select_for_update()
                                .get(
                                    id=product_id,
                                    is_active=True,
                                )
                            )
                        except Product.DoesNotExist:
                            raise ValueError(
                                "Mahsulot topilmadi."
                            )

                        quantity = item[
                            "quantity"
                        ]

                        if product.stock < quantity:
                            raise ValueError(
                                f"{product.name} omborda yetarli emas."
                            )

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            product_name=product.name,
                            price=product.price,
                            quantity=quantity,
                        )

                        product.stock -= quantity

                        product.save(
                            update_fields=[
                                "stock",
                            ]
                        )

                        final_total += (
                            product.price
                            * quantity
                        )

                    order.total_price = final_total

                    order.save(
                        update_fields=[
                            "total_price",
                        ]
                    )

                clear_cart(request)

                return redirect(
                    "shop:order-success",
                    order_id=order.id,
                )

            except ValueError as error:
                messages.error(
                    request,
                    str(error),
                )
    else:
        form = CheckoutForm(
            initial={
                "first_name": (
                    request.user.first_name
                    or request.user.username
                ),
            }
        )

    return render(
        request,
        "shop/checkout.html",
        {
            "form": form,
            "items": items,
            "total": total,
        },
    )


@login_required
def order_success(
    request,
    order_id,
):
    order = get_object_or_404(
        Order.objects.prefetch_related(
            "items",
        ),
        id=order_id,
        user=request.user,
    )

    return render(
        request,
        "shop/order_success.html",
        {
            "order": order,
        },
    )


@login_required
def my_orders(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related("items")
    )

    return render(
        request,
        "shop/my_orders.html",
        {
            "orders": orders,
        },
    )