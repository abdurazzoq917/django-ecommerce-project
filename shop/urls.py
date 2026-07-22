from django.urls import path

from . import views


app_name = "shop"


urlpatterns = [
    path(
        "",
        views.product_list,
        name="product-list",
    ),
    path(
        "product/<slug:slug>/",
        views.product_detail,
        name="product-detail",
    ),
    path(
        "cart/",
        views.cart_detail,
        name="cart",
    ),
    path(
        "cart/add/<int:product_id>/",
        views.cart_add,
        name="cart-add",
    ),
    path(
        "cart/remove/<int:product_id>/",
        views.cart_remove,
        name="cart-remove",
    ),
    path(
        "checkout/",
        views.checkout,
        name="checkout",
    ),
    path(
        "orders/",
        views.my_orders,
        name="my-orders",
    ),
    path(
        "order/<int:order_id>/success/",
        views.order_success,
        name="order-success",
    ),
]