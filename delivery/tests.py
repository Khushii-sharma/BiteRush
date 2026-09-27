from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse
from razorpay.errors import BadRequestError

from .models import Cart, Customer, Item, Restaurant


class CheckoutTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            username='checkout-user',
            password='password',
            email='checkout@example.com',
            mobile='1234567890',
            address='Test address',
        )
        restaurant = Restaurant.objects.create(
            name='Test restaurant',
            cuisine='Test',
            rating=4.5,
        )
        item = Item.objects.create(
            restaurant=restaurant,
            name='Test item',
            description='Test item',
            price=25.5,
        )
        self.cart = Cart.objects.create(customer=self.customer)
        self.cart.items.add(item)
        self.url = reverse('checkout', kwargs={'username': self.customer.username})

    @override_settings(RAZORPAY_KEY_ID='', RAZORPAY_KEY_SECRET='')
    @patch('delivery.views.razorpay.Client')
    def test_missing_credentials_render_configuration_error(self, razorpay_client):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Online payments are not configured')
        razorpay_client.assert_not_called()

    @override_settings(
        RAZORPAY_KEY_ID='rzp_test_configured',
        RAZORPAY_KEY_SECRET='test-secret',
    )
    @patch('delivery.views.razorpay.Client')
    def test_checkout_uses_configured_key_and_order_amount(self, razorpay_client):
        razorpay_client.return_value.order.create.return_value = {
            'id': 'order_test123',
            'amount': 2550,
        }

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '"key": "rzp_test_configured"')
        self.assertContains(response, '"amount": 2550')
        razorpay_client.assert_called_once_with(
            auth=('rzp_test_configured', 'test-secret'),
        )
        razorpay_client.return_value.order.create.assert_called_once_with(data={
            'amount': 2550,
            'currency': 'INR',
            'payment_capture': '1',
        })

    @override_settings(
        RAZORPAY_KEY_ID='rzp_test_configured',
        RAZORPAY_KEY_SECRET='wrong-secret',
    )
    @patch('delivery.views.razorpay.Client')
    def test_authentication_failure_renders_actionable_error(self, razorpay_client):
        razorpay_client.return_value.order.create.side_effect = BadRequestError(
            'Authentication failed',
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Razorpay could not authenticate these credentials')
        self.assertNotContains(response, 'wrong-secret')
