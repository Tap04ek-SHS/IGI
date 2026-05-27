from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from realty.models import (
    Amenity,
    Article,
    Buyer,
    Category,
    CompanyInfo,
    CompanyMilestone,
    CompanyRequisite,
    Employee,
    FAQ,
    Owner,
    PromoCode,
    Property,
    Review,
    Sale,
    Vacancy,
)


class Command(BaseCommand):
    help = "Заполняет базу демонстрационными данными для лабораторной работы"

    def handle(self, *args, **options):
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@realty.test", "is_staff": True, "is_superuser": True},
        )
        if created:
            admin.set_password("admin12345")
            admin.save()

        agent_user, _ = User.objects.get_or_create(
            username="agent",
            defaults={"email": "agent@realty.test", "is_staff": True},
        )
        agent_user.set_password("agent12345")
        agent_user.save()

        client_user, _ = User.objects.get_or_create(username="client", defaults={"email": "client@realty.test"})
        client_user.set_password("client12345")
        client_user.save()

        company, _ = CompanyInfo.objects.update_or_create(
            name="Domovita Realty",
            defaults={
                "description": "Агентство сопровождает покупку и продажу квартир, домов и коммерческих помещений в Минске.",
                "logo_url": "https://placehold.co/300x120?text=Domovita",
                "video_url": "https://example.com/company-video",
            },
        )
        CompanyMilestone.objects.update_or_create(company=company, year=2016, defaults={"title": "Открытие агентства"})
        CompanyMilestone.objects.update_or_create(company=company, year=2021, defaults={"title": "Запуск онлайн-каталога"})
        CompanyRequisite.objects.update_or_create(company=company, name="УНП", defaults={"value": "192837465"})
        CompanyRequisite.objects.update_or_create(company=company, name="Адрес", defaults={"value": "г. Минск, ул. Немига, 5"})

        categories = {}
        for name in ("Квартиры", "Дома", "Коммерческая недвижимость", "Новостройки"):
            categories[name], _ = Category.objects.get_or_create(name=name, defaults={"description": f"Раздел: {name.lower()}"})

        amenities = {}
        for name in ("Паркинг", "Лифт", "Метро рядом", "Балкон", "Ремонт", "Охрана"):
            amenities[name], _ = Amenity.objects.get_or_create(name=name)

        employee, _ = Employee.objects.update_or_create(
            user=agent_user,
            defaults={
                "first_name": "Анна",
                "last_name": "Ковалева",
                "job_title": "Ведущий агент",
                "birth_date": date(1990, 5, 12),
                "phone": "+375 (29) 111-22-33",
                "email": "agent@realty.test",
                "photo_url": "",
                "responsibilities": "Оценка объектов, сопровождение сделок, переговоры с клиентами.",
            },
        )

        owners = []
        for index in range(1, 7):
            owner, _ = Owner.objects.update_or_create(
                email=f"owner{index}@example.com",
                defaults={
                    "full_name": f"Владелец {index}",
                    "birth_date": date(1980, index, 10),
                    "phone": f"+375 (29) 22{index}-10-1{index}",
                },
            )
            owners.append(owner)

        buyers = []
        buyer_main, _ = Buyer.objects.update_or_create(
            user=client_user,
            defaults={
                "full_name": "Иван Петров",
                "birth_date": date(1995, 3, 20),
                "phone": "+375 (29) 333-44-55",
                "email": "client@realty.test",
            },
        )
        buyers.append(buyer_main)
        for index in range(2, 7):
            buyer, _ = Buyer.objects.update_or_create(
                email=f"buyer{index}@example.com",
                defaults={
                    "full_name": f"Покупатель {index}",
                    "birth_date": date(1992, index, 15),
                    "phone": f"+375 (33) 44{index}-20-2{index}",
                },
            )
            buyers.append(buyer)

        property_specs = [
            ("Квартира у парка", "Квартиры", 185000, 64, 2),
            ("Студия возле метро", "Квартиры", 125000, 38, 1),
            ("Дом в Зеленом бору", "Дома", 320000, 140, 5),
            ("Офис на проспекте", "Коммерческая недвижимость", 410000, 210, 8),
            ("Новостройка с видом", "Новостройки", 210000, 72, 3),
            ("Таунхаус для семьи", "Дома", 280000, 118, 4),
            ("Помещение под магазин", "Коммерческая недвижимость", 360000, 180, 6),
            ("Трехкомнатная квартира", "Квартиры", 240000, 86, 3),
            ("Апартаменты в центре", "Новостройки", 295000, 78, 2),
            ("Дом у озера", "Дома", 510000, 190, 6),
        ]
        properties = []
        for index, (title, category_name, price, area, rooms) in enumerate(property_specs, start=1):
            item, _ = Property.objects.update_or_create(
                title=title,
                defaults={
                    "category": categories[category_name],
                    "owner": owners[index % len(owners)],
                    "assigned_agent": employee,
                    "address": f"ул. Примерная, {index}",
                    "city": "Минск",
                    "price": Decimal(price),
                    "area": Decimal(area),
                    "rooms": rooms,
                    "floor": min(index, 9),
                    "total_floors": 12,
                    "description": "Объект с понятной историей владения и готовыми документами для сделки.",
                    "image_url": f"https://placehold.co/640x420?text=Property+{index}" if index % 3 == 0 else "",
                    "status": Property.Status.ACTIVE,
                },
            )
            item.amenities.set([amenities["Лифт"], amenities["Метро рядом"], amenities["Ремонт"]])
            properties.append(item)

        for index, item in enumerate(properties[:4], start=1):
            Sale.objects.update_or_create(
                property=item,
                defaults={
                    "buyer": buyers[index % len(buyers)],
                    "employee": employee,
                    "sold_at": timezone.localdate() - timedelta(days=index * 7),
                    "contract_date": timezone.localdate() - timedelta(days=index * 7 + 1),
                    "final_price": item.price - Decimal(index * 1500),
                    "commission_percent": Decimal("3.00"),
                },
            )

        for index in range(1, 6):
            Article.objects.update_or_create(
                title=f"Совет покупателю #{index}",
                defaults={
                    "summary": "Краткий совет по выбору и проверке недвижимости.",
                    "body": "Перед сделкой проверьте документы, историю объекта, условия оплаты и сроки освобождения помещения.",
                    "image_url": f"https://placehold.co/640x360?text=News+{index}" if index % 2 == 0 else "",
                    "is_published": True,
                    "published_at": timezone.now() - timedelta(days=index),
                },
            )

        faq_items = {
            "Задаток": "Сумма, подтверждающая намерение покупателя заключить сделку.",
            "Договор купли-продажи": "Документ, фиксирующий переход права собственности.",
            "Комиссия агентства": "Вознаграждение за подбор объекта и сопровождение сделки.",
        }
        for question, answer in faq_items.items():
            FAQ.objects.update_or_create(question=question, defaults={"answer": answer})

        Vacancy.objects.update_or_create(
            title="Агент по недвижимости",
            defaults={"description": "Поиск объектов, работа с клиентами, проведение показов.", "salary_from": 1800, "salary_to": 4500},
        )
        Vacancy.objects.update_or_create(
            title="Специалист по рекламе",
            defaults={"description": "Подготовка объявлений и продвижение объектов.", "salary_from": 1600, "salary_to": 2800},
        )

        Review.objects.update_or_create(
            user=client_user,
            name="Иван Петров",
            defaults={"rating": 5, "text": "Быстро подобрали квартиру и помогли пройти сделку без задержек."},
        )
        for index in range(2, 5):
            Review.objects.update_or_create(
                name=f"Клиент {index}",
                defaults={"rating": 4, "text": "Понравилась прозрачная работа с документами и понятная коммуникация."},
            )

        promo_active, _ = PromoCode.objects.update_or_create(
            code="HOME2026",
            defaults={
                "description": "Скидка на юридическое сопровождение сделки.",
                "discount_percent": 10,
                "valid_from": timezone.localdate(),
                "valid_to": timezone.localdate() + timedelta(days=60),
                "is_active": True,
            },
        )
        promo_active.categories.set([categories["Квартиры"], categories["Дома"]])
        promo_archive, _ = PromoCode.objects.update_or_create(
            code="SPRINGSALE",
            defaults={
                "description": "Архивная весенняя акция.",
                "discount_percent": 7,
                "valid_from": timezone.localdate() - timedelta(days=120),
                "valid_to": timezone.localdate() - timedelta(days=30),
                "is_active": False,
            },
        )
        promo_archive.categories.set([categories["Новостройки"]])

        self.stdout.write(self.style.SUCCESS("Демо-данные созданы. admin/admin12345, agent/agent12345, client/client12345"))
