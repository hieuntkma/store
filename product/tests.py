from django.test import TestCase
from rest_framework.test import APIClient
from product.models import Product
from uuid import uuid4

class ProductDetailAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.product = Product.objects.create(
            uuid=uuid4(),
            name="Test Product",
            product_name="Sản phẩm test",
            desc="Mô tả test",
            price=100000,
            sale_price=80000,
            stock_quantity=5,
            quantity=1,
            active=True
        )

    def test_get_valid_product_detail(self):
        response = self.client.get(f'/product/api/detail/{self.product.uuid}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], "Test Product")

    def test_get_invalid_product_detail(self):
        fake_uuid = uuid4()
        response = self.client.get(f'/product/api/detail/{fake_uuid}/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data()['error'], "Product not found")
