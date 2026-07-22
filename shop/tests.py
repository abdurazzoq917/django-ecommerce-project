from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import (
    Category,
    Product,
)


class ShopTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Telefonlar",
            slug="telefonlar",
        )

        self.product = Product.objects.create(
            category=self.category,
            name="Smartphone",
            slug="smartphone",
            price=1000000,
            stock=5,
        )

        self.user = User.objects.create_user(
            username="ali",
            password="TestPassword123",
        )

    def test_product_list(self):
        response = self.client.get(
            reverse("shop:product-list"),
        )

        self.assertContains(
            response,
            "Smartphone",
        )

    def test_add_product_to_cart(self):
        response = self.client.post(
            reverse(
                "shop:cart-add",
                args=[self.product.id],
            ),
            {
                "quantity": 2,
            },
        )

        self.assertRedirects(
            response,
            reverse("shop:cart"),
        )

        cart = self.client.session["cart"]

        self.assertEqual(
            cart[str(self.product.id)],
            2,
        )

    def test_checkout_requires_login(self):
        session = self.client.session

        session["cart"] = {
            str(self.product.id): 1,
        }

        session.save()

        response = self.client.get(
            reverse("shop:checkout"),
        )

        self.assertEqual(
            response.status_code,
            302,
        )