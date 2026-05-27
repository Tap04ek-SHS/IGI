from datetime import date
from builtins import property as builtin_property

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


phone_validator = RegexValidator(
    regex=r"^\+375 \((29|25|33|44)\) \d{3}-\d{2}-\d{2}$",
    message="Телефон должен быть в формате +375 (29) XXX-XX-XX",
)


def validate_adult(value):
    today = date.today()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 18:
        raise ValidationError("Возраст должен быть 18+")


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("создано", auto_now_add=True)
    updated_at = models.DateTimeField("изменено", auto_now=True)

    class Meta:
        abstract = True


class CompanyInfo(TimeStampedModel):
    name = models.CharField("название", max_length=120)
    description = models.TextField("описание")
    logo = models.ImageField(
        "загрузить файл логотипа",
        upload_to="company/",
        blank=True,
        help_text="Файл логотипа компании с компьютера.",
    )
    logo_url = models.URLField(
        "ссылка на логотип",
        blank=True,
        help_text="Прямая ссылка на логотип, если файл не загружен.",
    )
    video_url = models.URLField("видео", blank=True)

    class Meta:
        verbose_name = "информация о компании"
        verbose_name_plural = "информация о компании"

    def __str__(self):
        return self.name

    @builtin_property
    def display_logo_url(self):
        if self.logo:
            return self.logo.url
        return self.logo_url


class CompanyMilestone(models.Model):
    company = models.ForeignKey(
        CompanyInfo,
        verbose_name="компания",
        related_name="milestones",
        on_delete=models.CASCADE,
    )
    year = models.PositiveSmallIntegerField("год")
    title = models.CharField("событие", max_length=150)
    description = models.TextField("описание", blank=True)

    class Meta:
        ordering = ["year"]
        verbose_name = "этап истории"
        verbose_name_plural = "история компании"

    def __str__(self):
        return f"{self.year}: {self.title}"


class CompanyRequisite(models.Model):
    company = models.ForeignKey(
        CompanyInfo,
        verbose_name="компания",
        related_name="requisites",
        on_delete=models.CASCADE,
    )
    name = models.CharField("поле", max_length=80)
    value = models.CharField("значение", max_length=255)

    class Meta:
        verbose_name = "реквизит"
        verbose_name_plural = "реквизиты"

    def __str__(self):
        return f"{self.name}: {self.value}"


class Article(TimeStampedModel):
    title = models.CharField("заголовок", max_length=200)
    summary = models.CharField("краткое содержание", max_length=255)
    body = models.TextField("текст статьи")
    image = models.ImageField(
        "загрузить файл картинки",
        upload_to="articles/",
        blank=True,
        help_text="Файл картинки новости с компьютера.",
    )
    image_url = models.URLField(
        "ссылка на картинку",
        blank=True,
        help_text="Прямая ссылка на картинку, если файл не загружен.",
    )
    published_at = models.DateTimeField("дата публикации", default=timezone.now)
    is_published = models.BooleanField("опубликовано", default=True)

    class Meta:
        ordering = ["-published_at"]
        verbose_name = "новость"
        verbose_name_plural = "новости"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("article_detail", kwargs={"pk": self.pk})

    @builtin_property
    def display_image_url(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return reverse("article_generated_image", kwargs={"pk": self.pk})


class FAQ(TimeStampedModel):
    question = models.CharField("вопрос", max_length=255)
    answer = models.TextField("ответ")
    added_at = models.DateField("дата добавления", default=timezone.localdate)

    class Meta:
        ordering = ["question"]
        verbose_name = "термин/вопрос"
        verbose_name_plural = "словарь терминов"

    def __str__(self):
        return self.question


class Category(TimeStampedModel):
    name = models.CharField("категория", max_length=100, unique=True)
    description = models.TextField("описание", blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "категория"
        verbose_name_plural = "категории"

    def __str__(self):
        return self.name


class Amenity(models.Model):
    name = models.CharField("удобство", max_length=80, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "удобство"
        verbose_name_plural = "удобства"

    def __str__(self):
        return self.name


class Employee(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="пользователь",
        related_name="employee_profile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    first_name = models.CharField("имя", max_length=80)
    last_name = models.CharField("фамилия", max_length=80)
    job_title = models.CharField("должность", max_length=120)
    birth_date = models.DateField("дата рождения", validators=[validate_adult])
    phone = models.CharField("телефон", max_length=19, validators=[phone_validator])
    email = models.EmailField("email")
    photo = models.ImageField(
        "загрузить файл фото",
        upload_to="employees/",
        blank=True,
        help_text="Файл фотографии сотрудника с компьютера.",
    )
    photo_url = models.URLField(
        "ссылка на фото",
        blank=True,
        help_text="Прямая ссылка на фото, если файл не загружен.",
    )
    responsibilities = models.TextField("выполняемые работы")
    hire_date = models.DateField("дата приема", default=timezone.localdate)

    class Meta:
        ordering = ["last_name", "first_name"]
        verbose_name = "сотрудник"
        verbose_name_plural = "сотрудники"

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    @builtin_property
    def display_photo_url(self):
        if self.photo:
            return self.photo.url
        if self.photo_url:
            return self.photo_url
        return reverse("employee_generated_photo", kwargs={"pk": self.pk})


class Owner(TimeStampedModel):
    full_name = models.CharField("ФИО", max_length=160)
    birth_date = models.DateField("дата рождения", validators=[validate_adult])
    phone = models.CharField("телефон", max_length=19, validators=[phone_validator])
    email = models.EmailField("email")

    class Meta:
        ordering = ["full_name"]
        verbose_name = "владелец"
        verbose_name_plural = "владельцы"

    def __str__(self):
        return self.full_name


class Buyer(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="пользователь",
        related_name="buyer_profile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    full_name = models.CharField("ФИО", max_length=160)
    birth_date = models.DateField("дата рождения", validators=[validate_adult])
    phone = models.CharField("телефон", max_length=19, validators=[phone_validator])
    email = models.EmailField("email")

    class Meta:
        ordering = ["full_name"]
        verbose_name = "покупатель"
        verbose_name_plural = "покупатели"

    def __str__(self):
        return self.full_name


class Property(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "В продаже"
        RESERVED = "reserved", "Зарезервировано"
        SOLD = "sold", "Продано"
        ARCHIVED = "archived", "Архив"

    title = models.CharField("название", max_length=180)
    category = models.ForeignKey(
        Category,
        verbose_name="категория",
        related_name="properties",
        on_delete=models.PROTECT,
    )
    owner = models.ForeignKey(
        Owner,
        verbose_name="владелец",
        related_name="properties",
        on_delete=models.PROTECT,
    )
    assigned_agent = models.ForeignKey(
        Employee,
        verbose_name="сотрудник",
        related_name="properties",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    amenities = models.ManyToManyField(Amenity, verbose_name="удобства", blank=True)
    address = models.CharField("адрес", max_length=255)
    city = models.CharField("город", max_length=80, default="Минск")
    price = models.DecimalField("цена, BYN", max_digits=12, decimal_places=2)
    area = models.DecimalField("площадь, м2", max_digits=8, decimal_places=2)
    rooms = models.PositiveSmallIntegerField("комнат", validators=[MinValueValidator(1)])
    floor = models.PositiveSmallIntegerField("этаж", validators=[MinValueValidator(1)])
    total_floors = models.PositiveSmallIntegerField("этажей", validators=[MinValueValidator(1)])
    description = models.TextField("описание")
    image = models.ImageField(
        "загрузить файл картинки",
        upload_to="properties/",
        blank=True,
        help_text="Выберите файл с компьютера. Это поле важнее ссылки ниже.",
    )
    image_url = models.URLField(
        "ссылка на картинку",
        blank=True,
        help_text="Можно вставить прямую ссылку на изображение. Если файл не загружен, будет использована эта ссылка.",
    )
    status = models.CharField(
        "статус",
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    class Meta:
        ordering = ["title"]
        verbose_name = "объект недвижимости"
        verbose_name_plural = "объекты недвижимости"

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        if self.floor and self.total_floors and self.floor > self.total_floors:
            raise ValidationError({"floor": "Этаж не может быть больше общего числа этажей"})

    def get_absolute_url(self):
        return reverse("property_detail", kwargs={"pk": self.pk})

    @builtin_property
    def display_image_url(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return reverse("property_generated_image", kwargs={"pk": self.pk})


class Sale(TimeStampedModel):
    property = models.OneToOneField(
        Property,
        verbose_name="объект",
        related_name="sale",
        on_delete=models.PROTECT,
    )
    buyer = models.ForeignKey(
        Buyer,
        verbose_name="покупатель",
        related_name="sales",
        on_delete=models.PROTECT,
    )
    employee = models.ForeignKey(
        Employee,
        verbose_name="сотрудник",
        related_name="sales",
        on_delete=models.PROTECT,
    )
    sold_at = models.DateField("дата продажи", default=timezone.localdate)
    contract_date = models.DateField("дата договора", default=timezone.localdate)
    final_price = models.DecimalField("сумма сделки, BYN", max_digits=12, decimal_places=2)
    commission_percent = models.DecimalField(
        "комиссия, %",
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=3,
    )

    class Meta:
        ordering = ["-sold_at"]
        verbose_name = "продажа"
        verbose_name_plural = "продажи"

    def __str__(self):
        return f"{self.property} - {self.final_price} BYN"

    @builtin_property
    def commission_amount(self):
        return self.final_price * self.commission_percent / 100

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.property.status != Property.Status.SOLD:
            self.property.status = Property.Status.SOLD
            self.property.save(update_fields=["status", "updated_at"])


class Vacancy(TimeStampedModel):
    title = models.CharField("вакансия", max_length=160)
    description = models.TextField("описание")
    salary_from = models.DecimalField("зарплата от", max_digits=10, decimal_places=2, null=True, blank=True)
    salary_to = models.DecimalField("зарплата до", max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField("активна", default=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "вакансия"
        verbose_name_plural = "вакансии"

    def __str__(self):
        return self.title


class Review(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="пользователь",
        related_name="reviews",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    name = models.CharField("имя", max_length=100)
    rating = models.PositiveSmallIntegerField(
        "оценка",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    text = models.TextField("текст")
    added_at = models.DateField("дата", default=timezone.localdate)
    is_published = models.BooleanField("опубликовано", default=True)

    class Meta:
        ordering = ["-added_at", "-created_at"]
        verbose_name = "отзыв"
        verbose_name_plural = "отзывы"

    def __str__(self):
        return f"{self.name}: {self.rating}"


class PromoCode(TimeStampedModel):
    code = models.CharField("код", max_length=40, unique=True)
    description = models.TextField("описание")
    discount_percent = models.PositiveSmallIntegerField(
        "скидка, %",
        validators=[MinValueValidator(1), MaxValueValidator(100)],
    )
    categories = models.ManyToManyField(Category, verbose_name="категории", blank=True)
    valid_from = models.DateField("действует с")
    valid_to = models.DateField("действует до")
    is_active = models.BooleanField("активен", default=True)

    class Meta:
        ordering = ["-is_active", "valid_to"]
        verbose_name = "промокод"
        verbose_name_plural = "промокоды и купоны"

    def __str__(self):
        return self.code

    @property
    def is_archived(self):
        return not self.is_active or self.valid_to < timezone.localdate()

# Create your models here.
