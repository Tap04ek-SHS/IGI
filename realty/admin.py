from django.contrib import admin
from django.utils.html import format_html

from .forms import PropertyForm
from .models import (
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


class CompanyMilestoneInline(admin.TabularInline):
    model = CompanyMilestone
    extra = 1


class CompanyRequisiteInline(admin.TabularInline):
    model = CompanyRequisite
    extra = 1


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ("name", "updated_at", "logo_source")
    readonly_fields = ("logo_preview",)
    fieldsets = (
        ("Основное", {"fields": ("name", "description", "video_url")}),
        (
            "Логотип",
            {
                "fields": ("logo", "logo_url", "logo_preview"),
                "description": "Логотип необязателен. Можно загрузить файл или вставить ссылку.",
            },
        ),
    )
    inlines = (CompanyMilestoneInline, CompanyRequisiteInline)

    @admin.display(description="логотип")
    def logo_source(self, obj):
        if obj.logo:
            return "файл"
        if obj.logo_url:
            return "ссылка"
        return "нет"

    @admin.display(description="предпросмотр")
    def logo_preview(self, obj):
        if not obj.pk:
            return "Предпросмотр появится после сохранения."
        if not obj.display_logo_url:
            return "Логотип не задан."
        return format_html('<img src="{}" alt="{}" width="240">', obj.display_logo_url, obj.name)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "published_at", "is_published", "image_source")
    list_filter = ("is_published", "published_at")
    search_fields = ("title", "summary", "body")
    date_hierarchy = "published_at"
    readonly_fields = ("image_preview",)
    fieldsets = (
        ("Текст", {"fields": ("title", "summary", "body", "published_at", "is_published")}),
        (
            "Картинка",
            {
                "fields": ("image", "image_url", "image_preview"),
                "description": "Для новости можно загрузить файл или вставить ссылку. Если ничего не заполнено, сайт сгенерирует картинку автоматически.",
            },
        ),
    )

    @admin.display(description="картинка")
    def image_source(self, obj):
        if obj.image:
            return "файл"
        if obj.image_url:
            return "ссылка"
        return "авто"

    @admin.display(description="предпросмотр")
    def image_preview(self, obj):
        if not obj.pk:
            return "Предпросмотр появится после сохранения."
        return format_html('<img src="{}" alt="{}" width="240">', obj.display_image_url, obj.title)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "added_at")
    search_fields = ("question", "answer")
    list_filter = ("added_at",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "job_title", "phone", "email", "photo_source")
    list_filter = ("job_title", "hire_date")
    search_fields = ("first_name", "last_name", "phone", "email")
    readonly_fields = ("photo_preview",)
    fieldsets = (
        (
            "Основное",
            {
                "fields": (
                    "user",
                    "first_name",
                    "last_name",
                    "job_title",
                    "birth_date",
                    "phone",
                    "email",
                    "responsibilities",
                    "hire_date",
                )
            },
        ),
        (
            "Фото",
            {
                "fields": ("photo", "photo_url", "photo_preview"),
                "description": "Для контактов можно загрузить файл фото или вставить ссылку. Если ничего не заполнено, сайт сгенерирует фото-заглушку автоматически.",
            },
        ),
    )

    @admin.display(description="фото")
    def photo_source(self, obj):
        if obj.photo:
            return "файл"
        if obj.photo_url:
            return "ссылка"
        return "авто"

    @admin.display(description="предпросмотр")
    def photo_preview(self, obj):
        if not obj.pk:
            return "Предпросмотр появится после сохранения."
        return format_html('<img src="{}" alt="{}" width="180">', obj.display_photo_url, obj)


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "email")
    search_fields = ("full_name", "phone", "email")


@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "email")
    search_fields = ("full_name", "phone", "email")


class SaleInline(admin.TabularInline):
    model = Sale
    extra = 0
    readonly_fields = ("created_at", "updated_at")


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    form = PropertyForm
    list_display = ("title", "category", "owner", "assigned_agent", "price", "status", "image_source")
    list_filter = ("status", "category", "city", "assigned_agent")
    search_fields = ("title", "address", "description", "owner__full_name")
    filter_horizontal = ("amenities",)
    readonly_fields = ("image_preview",)
    fieldsets = (
        (
            "Основное",
            {
                "fields": (
                    "title",
                    "category",
                    "owner",
                    "assigned_agent",
                    "amenities",
                    "status",
                )
            },
        ),
        (
            "Адрес и характеристики",
            {
                "fields": (
                    "city",
                    "address",
                    "price",
                    "area",
                    "rooms",
                    "floor",
                    "total_floors",
                    "description",
                )
            },
        ),
        (
            "Картинка",
            {
                "fields": (
                    "image",
                    "image_url",
                    "image_preview",
                ),
                "description": "Можно загрузить файл с компьютера или вставить ссылку. Если ничего не заполнено, сайт сгенерирует картинку автоматически.",
            },
        ),
    )
    inlines = (SaleInline,)

    @admin.display(description="картинка")
    def image_source(self, obj):
        if obj.image:
            return "файл"
        if obj.image_url:
            return "ссылка"
        return "авто"

    @admin.display(description="предпросмотр")
    def image_preview(self, obj):
        if not obj.pk:
            return "Предпросмотр появится после сохранения объекта."
        return format_html('<img src="{}" alt="{}" width="240">', obj.display_image_url, obj.title)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("property", "buyer", "employee", "sold_at", "final_price", "commission_percent")
    list_filter = ("sold_at", "employee")
    search_fields = ("property__title", "buyer__full_name", "employee__last_name")
    date_hierarchy = "sold_at"


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ("title", "salary_from", "salary_to", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "description")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("name", "rating", "added_at", "is_published")
    list_filter = ("rating", "is_published", "added_at")
    search_fields = ("name", "text")


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_percent", "valid_from", "valid_to", "is_active")
    list_filter = ("is_active", "valid_to", "categories")
    search_fields = ("code", "description")
    filter_horizontal = ("categories",)

# Register your models here.
