from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Buyer, Property, Review, Sale, phone_validator, validate_adult


PHONE_PATTERN = r"^\+375 \((29|25|33|44)\) \d{3}-\d{2}-\d{2}$"


class BasicFormMixin:
    def _apply_base_attrs(self):
        return None


class PropertyForm(BasicFormMixin, forms.ModelForm):
    image = forms.ImageField(
        label="Загрузить файл картинки",
        required=False,
        help_text="Можно загрузить JPG, PNG, GIF или WebP с компьютера.",
        widget=forms.ClearableFileInput(attrs={"accept": "image/*"}),
    )
    image_url = forms.URLField(
        label="Ссылка на картинку",
        required=False,
        help_text="Вставьте прямую ссылку на изображение, если не хотите загружать файл.",
        widget=forms.URLInput(attrs={"placeholder": "https://example.com/image.jpg"}),
    )

    class Meta:
        model = Property
        fields = (
            "title",
            "category",
            "owner",
            "assigned_agent",
            "amenities",
            "address",
            "city",
            "price",
            "area",
            "rooms",
            "floor",
            "total_floors",
            "description",
            "image",
            "image_url",
            "status",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "amenities": forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_base_attrs()


class SaleForm(BasicFormMixin, forms.ModelForm):
    class Meta:
        model = Sale
        fields = ("property", "buyer", "employee", "sold_at", "contract_date", "final_price", "commission_percent")
        widgets = {
            "sold_at": forms.DateInput(attrs={"type": "date"}),
            "contract_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_base_attrs()


class ReviewForm(BasicFormMixin, forms.ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "text")
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5}),
            "text": forms.Textarea(attrs={"rows": 4, "minlength": 10}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_base_attrs()


class RegistrationForm(BasicFormMixin, UserCreationForm):
    full_name = forms.CharField(label="ФИО", max_length=160)
    birth_date = forms.DateField(
        label="Дата рождения",
        validators=[validate_adult],
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    phone = forms.CharField(
        label="Телефон",
        max_length=19,
        validators=[phone_validator],
        widget=forms.TextInput(attrs={"pattern": PHONE_PATTERN, "placeholder": "+375 (29) 123-45-67"}),
    )
    email = forms.EmailField(label="Email")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "full_name", "birth_date", "phone", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_base_attrs()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            Buyer.objects.create(
                user=user,
                full_name=self.cleaned_data["full_name"],
                birth_date=self.cleaned_data["birth_date"],
                phone=self.cleaned_data["phone"],
                email=self.cleaned_data["email"],
            )
        return user


class BuyerForm(BasicFormMixin, forms.ModelForm):
    class Meta:
        model = Buyer
        fields = ("full_name", "birth_date", "phone", "email")
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
            "phone": forms.TextInput(attrs={"pattern": PHONE_PATTERN, "placeholder": "+375 (29) 123-45-67"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_base_attrs()
