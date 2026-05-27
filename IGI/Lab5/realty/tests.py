from datetime import date
from decimal import Decimal
import shutil
import tempfile
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Article, Buyer, Category, CompanyInfo, Employee, Owner, Property, Review, Sale, phone_validator, validate_adult


TEST_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class RealtyTestCase(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_user("staff", password="Str0ngPass123", is_staff=True)
        cls.user = User.objects.create_user("client", password="Str0ngPass123", email="client@test.local")
        cls.category = Category.objects.create(name="Квартиры", description="Жилая недвижимость")
        cls.owner = Owner.objects.create(
            full_name="Петр Сидоров",
            birth_date=date(1980, 1, 1),
            phone="+375 (29) 123-45-67",
            email="owner@test.local",
        )
        cls.employee = Employee.objects.create(
            user=cls.staff,
            first_name="Анна",
            last_name="Ковалева",
            job_title="Агент",
            birth_date=date(1990, 1, 1),
            phone="+375 (33) 123-45-67",
            email="staff@test.local",
            responsibilities="Продажи",
        )
        cls.buyer = Buyer.objects.create(
            user=cls.user,
            full_name="Иван Иванов",
            birth_date=date(1995, 1, 1),
            phone="+375 (44) 123-45-67",
            email="client@test.local",
        )
        cls.property = Property.objects.create(
            title="Светлая квартира",
            category=cls.category,
            owner=cls.owner,
            assigned_agent=cls.employee,
            address="ул. Тестовая, 1",
            city="Минск",
            price=Decimal("150000"),
            area=Decimal("55.5"),
            rooms=2,
            floor=3,
            total_floors=9,
            description="Тестовый объект",
        )
        cls.article = Article.objects.create(
            title="Новость без картинки",
            summary="Краткая новость",
            body="Полный текст новости",
        )
        cls.company = CompanyInfo.objects.create(
            name="Тестовое агентство",
            description="Описание компании",
        )

    def test_phone_validator_accepts_required_format(self):
        phone_validator("+375 (29) 123-45-67")

    def test_phone_validator_rejects_invalid_format(self):
        with self.assertRaises(ValidationError):
            phone_validator("80291234567")

    def test_adult_validator_rejects_minor(self):
        with self.assertRaises(ValidationError):
            validate_adult(date.today())

    def test_property_floor_cannot_exceed_total_floors(self):
        self.property.floor = 10
        self.property.total_floors = 5
        with self.assertRaises(ValidationError):
            self.property.full_clean()

    def test_property_list_search_finds_object(self):
        response = self.client.get(reverse("property_list"), {"q": "Светлая"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Светлая квартира")

    def test_property_list_filters_by_price_and_rooms(self):
        response = self.client.get(reverse("property_list"), {"price_from": "140000", "price_to": "160000", "rooms": "2"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Светлая квартира")

    def test_property_without_image_has_generated_svg(self):
        response = self.client.get(reverse("property_generated_image", args=[self.property.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/svg+xml")
        self.assertContains(response, "Светлая квартира")

    def test_admin_property_form_has_image_upload_and_url_fields(self):
        admin_user = User.objects.create_superuser("admin2", "admin2@test.local", "Str0ngPass123")
        self.client.force_login(admin_user)
        response = self.client.get("/admin/realty/property/add/", HTTP_HOST="localhost")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'type="file"')
        self.assertContains(response, 'name="image"')
        self.assertContains(response, 'name="image_url"')
        self.assertContains(response, "Загрузить файл картинки")

    def test_admin_content_forms_have_file_upload_fields(self):
        admin_user = User.objects.create_superuser("admin3", "admin3@test.local", "Str0ngPass123")
        self.client.force_login(admin_user)
        checks = (
            ("/admin/realty/article/add/", 'name="image"', 'name="image_url"', "Картинка"),
            ("/admin/realty/employee/add/", 'name="photo"', 'name="photo_url"', "Фото"),
            ("/admin/realty/companyinfo/add/", 'name="logo"', 'name="logo_url"', "Логотип"),
        )
        for path, file_field, url_field, section in checks:
            with self.subTest(path=path):
                response = self.client.get(path, HTTP_HOST="localhost")
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'type="file"')
                self.assertContains(response, file_field)
                self.assertContains(response, url_field)
                self.assertContains(response, section)

    def test_article_and_employee_without_images_have_generated_svg(self):
        article_response = self.client.get(reverse("article_generated_image", args=[self.article.pk]))
        employee_response = self.client.get(reverse("employee_generated_photo", args=[self.employee.pk]))
        self.assertEqual(article_response.status_code, 200)
        self.assertEqual(employee_response.status_code, 200)
        self.assertEqual(article_response["Content-Type"], "image/svg+xml")
        self.assertEqual(employee_response["Content-Type"], "image/svg+xml")

    def test_property_api_requires_login(self):
        response = self.client.get(reverse("properties_api"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])

    def test_property_api_returns_data_for_authorized_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("properties_api"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"][0]["title"], "Светлая квартира")

    def test_non_staff_cannot_create_property(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("property_create"))
        self.assertEqual(response.status_code, 403)

    def test_staff_can_create_property(self):
        self.client.force_login(self.staff)
        image = SimpleUploadedFile(
            "house.gif",
            b"GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00\xff\xff\xff,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;",
            content_type="image/gif",
        )
        response = self.client.post(
            reverse("property_create"),
            {
                "title": "Новый дом",
                "category": self.category.id,
                "owner": self.owner.id,
                "assigned_agent": self.employee.id,
                "address": "ул. Новая, 5",
                "city": "Минск",
                "price": "250000",
                "area": "120",
                "rooms": "4",
                "floor": "1",
                "total_floors": "2",
                "description": "Дом для семьи",
                "image": image,
                "status": Property.Status.ACTIVE,
            },
        )
        self.assertEqual(response.status_code, 302)
        created = Property.objects.get(title="Новый дом")
        self.assertTrue(created.image.name.startswith("properties/"))

    def test_logged_user_can_create_review(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("review_create"), {"rating": "5", "text": "Отличная работа команды"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Review.objects.filter(user=self.user, rating=5).exists())

    def test_sale_marks_property_as_sold(self):
        Sale.objects.create(
            property=self.property,
            buyer=self.buyer,
            employee=self.employee,
            final_price=Decimal("145000"),
            commission_percent=Decimal("3"),
        )
        self.property.refresh_from_db()
        self.assertEqual(self.property.status, Property.Status.SOLD)

    def test_logged_user_can_buy_active_property(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("property_buy", args=[self.property.pk]))
        self.assertRedirects(response, reverse("profile"))
        self.property.refresh_from_db()
        self.assertEqual(self.property.status, Property.Status.SOLD)
        self.assertTrue(Sale.objects.filter(property=self.property, buyer=self.buyer).exists())

    def test_registration_creates_buyer_profile(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newclient",
                "email": "newclient@test.local",
                "full_name": "Новый Клиент",
                "birth_date": "1998-02-02",
                "phone": "+375 (25) 555-44-33",
                "password1": "VeryStr0ngPass123",
                "password2": "VeryStr0ngPass123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Buyer.objects.filter(full_name="Новый Клиент").exists())

    def test_invalid_timezone_falls_back_to_utc(self):
        response = self.client.get(reverse("timezone"), {"tz": "Bad/Zone"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "UTC")

    def test_external_services_uses_worldtime_when_available(self):
        def fake_fetch(url):
            if "worldtimeapi" in url:
                return {"timezone": "Europe/Minsk", "datetime": "2026-05-27T17:00:00+03:00"}
            return []

        with patch("realty.views.fetch_json", side_effect=fake_fetch):
            response = self.client.get(reverse("external_services"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "WorldTimeAPI")
        self.assertContains(response, "2026-05-27T17:00:00+03:00")

    def test_external_services_falls_back_to_timeapi(self):
        def fake_fetch(url):
            if "timeapi.io" in url:
                return {"timeZone": "Europe/Minsk", "dateTime": "2026-05-27T17:05:00"}
            return None

        with patch("realty.views.fetch_json", side_effect=fake_fetch):
            response = self.client.get(reverse("external_services"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TimeAPI.io")
        self.assertContains(response, "2026-05-27T17:05:00")
