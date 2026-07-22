from decimal import Decimal

from .models import Product


CART_SESSION_KEY = "cart"


def get_cart(request) -> dict:
    cart = request.session.get(
        CART_SESSION_KEY,
    )

    if cart is None:
        cart = {}
        request.session[CART_SESSION_KEY] = cart

    return cart


def save_cart(
    request,
    cart: dict,
) -> None:
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True


def clear_cart(request) -> None:
    request.session[CART_SESSION_KEY] = {}
    request.session.modified = True


def build_cart_items(request):
    cart = get_cart(request)

    product_ids = [
        int(product_id)
        for product_id in cart.keys()
    ]

    products = Product.objects.filter(
        id__in=product_ids,
        is_active=True,
    )

    items = []
    total = Decimal("0.00")

    for product in products:
        quantity = int(
            cart.get(
                str(product.id),
                0,
            )
        )

        if quantity <= 0:
            continue

        subtotal = product.price * quantity

        items.append(
            {
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal,
            }
        )

        total += subtotal

    return items, total