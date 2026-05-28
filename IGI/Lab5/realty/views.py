import base64
import calendar
import hashlib
import html
import json
import logging
import statistics
from io import BytesIO
from datetime import datetime
from urllib.error import URLError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Avg, Count, Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from .forms import BuyerForm, PropertyForm, RegistrationForm, ReviewForm, SaleForm
from .models import (
    Article,
    Buyer,
    Category,
    CompanyInfo,
    Employee,
    FAQ,
    PromoCode,
    Property,
    Review,
    Sale,
    Vacancy,
)

logger = logging.getLogger(__name__)


def _figure_to_base64(fig):
    buffer = BytesIO()
    FigureCanvasAgg(fig).print_png(buffer)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def _build_bar_chart(labels, values, title, ylabel):
    fig = Figure(figsize=(8, 4.5), constrained_layout=True)
    ax = fig.subplots()
    bars = ax.bar(labels, values, color="#4e79a7")
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", labelrotation=25)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.bar_label(bars, fmt="%.0f", padding=3)
    return _figure_to_base64(fig)


def _build_pie_chart(labels, values, title):
    fig = Figure(figsize=(7, 4.5), constrained_layout=True)
    ax = fig.subplots()
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.set_title(title)
    ax.axis("equal")
    return _figure_to_base64(fig)


def _build_histogram(values, title, xlabel):
    fig = Figure(figsize=(8, 4.5), constrained_layout=True)
    ax = fig.subplots()
    bins = min(8, max(1, len(values)))
    ax.hist(values, bins=bins, color="#59a14f", edgecolor="white")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Количество")
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    return _figure_to_base64(fig)


def fetch_json(url, timeout=4):
    request = Request(url, headers={"User-Agent": "Lab5Realty/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except (OSError, URLError, ValueError) as exc:
        logger.warning("External API request failed: %s", exc)
        return None


def fetch_minsk_time():
    world_time = fetch_json("https://worldtimeapi.org/api/timezone/Europe/Minsk")
    if world_time and world_time.get("datetime"):
        return {
            "provider": "WorldTimeAPI",
            "timezone": world_time.get("timezone", "Europe/Minsk"),
            "datetime": world_time["datetime"],
        }

    fallback_time = fetch_json("https://timeapi.io/api/time/current/zone?timeZone=Europe/Minsk")
    if fallback_time and fallback_time.get("dateTime"):
        return {
            "provider": "TimeAPI.io",
            "timezone": fallback_time.get("timeZone", "Europe/Minsk"),
            "datetime": fallback_time["dateTime"],
        }

    return {}


def generated_property_image(request, pk):
    property_item = get_object_or_404(Property.objects.select_related("category"), pk=pk)
    title = html.escape(property_item.title)
    category = html.escape(property_item.category.name)
    digest = hashlib.sha256(property_item.title.encode("utf-8")).hexdigest()
    background = f"#{digest[:6]}"
    accent = f"#{digest[6:12]}"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="640" height="420" viewBox="0 0 640 420" role="img" aria-label="{title}">
<rect width="640" height="420" fill="{background}"/>
<rect x="0" y="295" width="640" height="125" fill="{accent}" opacity="0.75"/>
<path d="M80 250 L320 90 L560 250 V330 H80 Z" fill="#ffffff" opacity="0.9"/>
<path d="M150 250 L320 140 L490 250 V330 H150 Z" fill="{background}" opacity="0.55"/>
<text x="320" y="365" text-anchor="middle" font-family="Arial, sans-serif" font-size="28" fill="#ffffff">{title}</text>
<text x="320" y="393" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="#ffffff">{category}</text>
</svg>"""
    return HttpResponse(svg, content_type="image/svg+xml")


def generated_article_image(request, pk):
    article = get_object_or_404(Article, pk=pk)
    title = html.escape(article.title)
    digest = hashlib.sha256(article.title.encode("utf-8")).hexdigest()
    background = f"#{digest[:6]}"
    accent = f"#{digest[6:12]}"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360" role="img" aria-label="{title}">
<rect width="640" height="360" fill="{background}"/>
<rect x="48" y="58" width="544" height="244" fill="#ffffff" opacity="0.9"/>
<rect x="88" y="96" width="464" height="32" fill="{accent}" opacity="0.8"/>
<rect x="88" y="154" width="330" height="22" fill="{background}" opacity="0.55"/>
<rect x="88" y="198" width="420" height="22" fill="{background}" opacity="0.35"/>
<text x="320" y="282" text-anchor="middle" font-family="Arial, sans-serif" font-size="26" fill="{background}">{title}</text>
</svg>"""
    return HttpResponse(svg, content_type="image/svg+xml")


def generated_employee_photo(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    name = html.escape(str(employee))
    initials = html.escape(f"{employee.first_name[:1]}{employee.last_name[:1]}".upper())
    digest = hashlib.sha256(str(employee).encode("utf-8")).hexdigest()
    background = f"#{digest[:6]}"
    accent = f"#{digest[6:12]}"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="480" height="360" viewBox="0 0 480 360" role="img" aria-label="{name}">
<rect width="480" height="360" fill="{background}"/>
<circle cx="240" cy="130" r="72" fill="#ffffff" opacity="0.9"/>
<circle cx="240" cy="116" r="34" fill="{accent}" opacity="0.85"/>
<path d="M145 245 C165 190 315 190 335 245 L335 292 L145 292 Z" fill="{accent}" opacity="0.85"/>
<text x="240" y="132" text-anchor="middle" font-family="Arial, sans-serif" font-size="32" fill="#ffffff">{initials}</text>
<text x="240" y="325" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" fill="#ffffff">{name}</text>
</svg>"""
    return HttpResponse(svg, content_type="image/svg+xml")


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


def home(request):
    latest_article = Article.objects.filter(is_published=True).first()
    featured_properties = Property.objects.select_related("category").filter(status=Property.Status.ACTIVE)[:3]
    return render(
        request,
        "realty/home.html",
        {"latest_article": latest_article, "featured_properties": featured_properties},
    )


def about(request):
    company = CompanyInfo.objects.prefetch_related("milestones", "requisites").first()
    return render(request, "realty/about.html", {"company": company})


class ArticleListView(ListView):
    model = Article
    template_name = "realty/article_list.html"
    context_object_name = "articles"

    def get_queryset(self):
        return Article.objects.filter(is_published=True)


class ArticleDetailView(DetailView):
    model = Article
    template_name = "realty/article_detail.html"
    context_object_name = "article"

    def get_queryset(self):
        return Article.objects.filter(is_published=True)


def faq_list(request):
    return render(request, "realty/faq_list.html", {"faqs": FAQ.objects.all()})


def contacts(request):
    return render(request, "realty/contacts.html", {"employees": Employee.objects.all()})


def privacy(request):
    return render(request, "realty/privacy.html")


def vacancies(request):
    return render(request, "realty/vacancies.html", {"vacancies": Vacancy.objects.all()})


def promos(request):
    active = PromoCode.objects.prefetch_related("categories").filter(is_active=True, valid_to__gte=timezone.localdate())
    archived = PromoCode.objects.prefetch_related("categories").exclude(id__in=active.values("id"))
    return render(request, "realty/promos.html", {"active_promos": active, "archived_promos": archived})


class PropertyListView(ListView):
    model = Property
    template_name = "realty/property_list.html"
    context_object_name = "properties"
    paginate_by = 20

    sort_fields = {
        "title": "title",
        "price": "price",
        "area": "area",
        "category": "category__name",
        "status": "status",
        "city": "city",
        "rooms": "rooms",
    }

    def get_queryset(self):
        queryset = Property.objects.select_related("category", "owner", "assigned_agent").prefetch_related("amenities")
        query = self.request.GET.get("q", "").strip()
        category = self.request.GET.get("category", "").strip()
        city = self.request.GET.get("city", "").strip()
        status = self.request.GET.get("status", "").strip()
        rooms = self.request.GET.get("rooms", "").strip()
        price_from = self.request.GET.get("price_from", "").strip()
        price_to = self.request.GET.get("price_to", "").strip()
        sort = self.request.GET.get("sort", "title")

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(address__icontains=query)
                | Q(city__icontains=query)
                | Q(description__icontains=query)
                | Q(owner__full_name__icontains=query)
            )
        if category:
            queryset = queryset.filter(category_id=category)
        if city:
            queryset = queryset.filter(city__icontains=city)
        if status:
            queryset = queryset.filter(status=status)
        if rooms:
            queryset = queryset.filter(rooms=rooms)
        if price_from:
            queryset = queryset.filter(price__gte=price_from)
        if price_to:
            queryset = queryset.filter(price__lte=price_to)
        return queryset.order_by(self.sort_fields.get(sort, "title"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["statuses"] = Property.Status.choices
        context["current_query"] = self.request.GET.get("q", "")
        context["current_category"] = self.request.GET.get("category", "")
        context["current_city"] = self.request.GET.get("city", "")
        context["current_status"] = self.request.GET.get("status", "")
        context["current_rooms"] = self.request.GET.get("rooms", "")
        context["current_price_from"] = self.request.GET.get("price_from", "")
        context["current_price_to"] = self.request.GET.get("price_to", "")
        context["current_sort"] = self.request.GET.get("sort", "title")
        return context


class PropertyDetailView(DetailView):
    model = Property
    template_name = "realty/property_detail.html"
    context_object_name = "property"

    def get_queryset(self):
        return Property.objects.select_related("category", "owner", "assigned_agent").prefetch_related("amenities")


@login_required
def property_buy_confirm(request, pk):
    property_item = get_object_or_404(
        Property.objects.select_related("category", "assigned_agent"),
        pk=pk,
    )
    return render(request, "realty/property_buy_confirm.html", {"property": property_item})


@require_POST
@login_required
def property_buy(request, pk):
    property_item = get_object_or_404(Property.objects.select_related("assigned_agent"), pk=pk)
    if property_item.status != Property.Status.ACTIVE or hasattr(property_item, "sale"):
        messages.error(request, "Этот объект уже недоступен для покупки.")
        return redirect(property_item)

    buyer, _ = Buyer.objects.get_or_create(
        user=request.user,
        defaults={
            "full_name": request.user.get_full_name() or request.user.username,
            "birth_date": "2000-01-01",
            "phone": "+375 (29) 000-00-00",
            "email": request.user.email or "client@example.com",
        },
    )
    employee = property_item.assigned_agent or Employee.objects.first()
    if not employee:
        messages.error(request, "Для объекта не назначен сотрудник. Свяжитесь с агентством.")
        return redirect(property_item)

    Sale.objects.create(
        property=property_item,
        buyer=buyer,
        employee=employee,
        final_price=property_item.price,
        commission_percent=3,
    )
    logger.info("User %s bought property %s", request.user.pk, property_item.pk)
    messages.success(request, "Покупка оформлена. Сделка появилась в личном кабинете.")
    return redirect("profile")


class PropertyCreateView(StaffRequiredMixin, CreateView):
    model = Property
    form_class = PropertyForm
    template_name = "realty/form.html"


class PropertyUpdateView(StaffRequiredMixin, UpdateView):
    model = Property
    form_class = PropertyForm
    template_name = "realty/form.html"


class PropertyDeleteView(StaffRequiredMixin, DeleteView):
    model = Property
    template_name = "realty/confirm_delete.html"
    success_url = reverse_lazy("property_list")


class SaleListView(StaffRequiredMixin, ListView):
    model = Sale
    template_name = "realty/sale_list.html"
    context_object_name = "sales"

    def get_queryset(self):
        return Sale.objects.select_related("property", "buyer", "employee")


class SaleCreateView(StaffRequiredMixin, CreateView):
    model = Sale
    form_class = SaleForm
    template_name = "realty/form.html"
    success_url = reverse_lazy("sale_list")


class SaleUpdateView(StaffRequiredMixin, UpdateView):
    model = Sale
    form_class = SaleForm
    template_name = "realty/form.html"
    success_url = reverse_lazy("sale_list")


class SaleDeleteView(StaffRequiredMixin, DeleteView):
    model = Sale
    template_name = "realty/confirm_delete.html"
    success_url = reverse_lazy("sale_list")


def reviews(request):
    return render(request, "realty/reviews.html", {"reviews": Review.objects.filter(is_published=True)})


@login_required
def review_create(request):
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.name = request.user.get_full_name() or request.user.username
            review.save()
            messages.success(request, "Отзыв сохранен.")
            return redirect("reviews")
    else:
        form = ReviewForm()
    return render(request, "realty/form.html", {"form": form, "title": "Добавить отзыв"})


@login_required
def profile(request):
    buyer, _ = Buyer.objects.get_or_create(
        user=request.user,
        defaults={
            "full_name": request.user.get_full_name() or request.user.username,
            "birth_date": "2000-01-01",
            "phone": "+375 (29) 000-00-00",
            "email": request.user.email or "client@example.com",
        },
    )
    if request.method == "POST":
        form = BuyerForm(request.POST, instance=buyer)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль обновлен.")
            return redirect("profile")
    else:
        form = BuyerForm(instance=buyer)
    purchases = Sale.objects.select_related("property").filter(buyer=buyer)
    return render(request, "realty/profile.html", {"form": form, "purchases": purchases})


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация завершена.")
            return redirect("profile")
    else:
        form = RegistrationForm()
    return render(request, "registration/register.html", {"form": form})


class RealtyLoginView(LoginView):
    template_name = "registration/login.html"


class RealtyLogoutView(LogoutView):
    pass


def statistics_view(request):
    sales = Sale.objects.select_related("property__category", "buyer", "employee")
    values = [float(value) for value in sales.values_list("final_price", flat=True)]
    today = timezone.localdate()
    ages = [
        today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        for birth_date in Buyer.objects.values_list("birth_date", flat=True)
    ]
    aggregate = sales.aggregate(total=Sum("final_price"), average=Avg("final_price"))
    median = statistics.median(values) if values else 0
    average_age = statistics.mean(ages) if ages else 0
    median_age = statistics.median(ages) if ages else 0
    try:
        mode = statistics.mode(values) if values else 0
    except statistics.StatisticsError:
        mode = 0

    by_category = list(
        sales.values("property__category__name")
        .annotate(total=Sum("final_price"), count=Count("id"))
        .order_by("-total")
    )
    most_popular_category = (
        sales.values("property__category__name")
        .annotate(count=Count("id"))
        .order_by("-count")
        .first()
    )
    chart_labels = [row["property__category__name"] for row in by_category]
    chart_values = [float(row["total"]) for row in by_category]
    chart_counts = [row["count"] for row in by_category]
    charts = {}
    if chart_values:
        charts["sales_by_category"] = _build_bar_chart(
            chart_labels,
            chart_values,
            "Сумма продаж по категориям",
            "Сумма, BYN",
        )
        charts["sales_count_by_category"] = _build_pie_chart(
            chart_labels,
            chart_counts,
            "Доля сделок по категориям",
        )
    if values:
        charts["sales_distribution"] = _build_histogram(
            values,
            "Распределение сумм сделок",
            "Сумма сделки, BYN",
        )
    if ages:
        charts["buyer_age_distribution"] = _build_histogram(
            ages,
            "Распределение возраста покупателей",
            "Возраст, лет",
        )

    context = {
        "buyers": Buyer.objects.order_by("full_name"),
        "total_sales": aggregate["total"] or 0,
        "average_sale": aggregate["average"] or 0,
        "median_sale": median,
        "mode_sale": mode,
        "average_age": average_age,
        "median_age": median_age,
        "by_category": by_category,
        "most_profitable_category": by_category[0] if by_category else None,
        "most_popular_category": most_popular_category,
        "charts": charts,
    }
    return render(request, "realty/statistics.html", context)


def timezone_view(request):
    tz_name = request.GET.get("tz", "Europe/Minsk")
    try:
        user_timezone = ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        tz_name = "UTC"
        user_timezone = ZoneInfo("UTC")

    now_utc = timezone.now()
    now_local = now_utc.astimezone(user_timezone)
    text_calendar = calendar.TextCalendar(firstweekday=0).formatmonth(now_local.year, now_local.month)
    return render(
        request,
        "realty/timezone.html",
        {
            "tz_name": tz_name,
            "now_utc": now_utc,
            "now_local": now_local,
            "text_calendar": text_calendar,
        },
    )


def external_services(request):
    rates = fetch_json("https://api.nbrb.by/exrates/rates?periodicity=0") or []
    world_time = fetch_minsk_time()
    selected_rates = [rate for rate in rates if rate.get("Cur_Abbreviation") in {"USD", "EUR", "RUB"}]
    return render(
        request,
        "realty/external_services.html",
        {
            "rates": selected_rates,
            "world_time": world_time,
            "api_checked_at": datetime.utcnow(),
        },
    )


@require_GET
@login_required
def properties_api(request):
    queryset = Property.objects.select_related("category").all()
    data = [
        {
            "id": item.id,
            "title": item.title,
            "category": item.category.name,
            "city": item.city,
            "price": str(item.price),
            "status": item.get_status_display(),
            "image": request.build_absolute_uri(item.display_image_url),
            "updated_at": item.updated_at.isoformat(),
        }
        for item in queryset
    ]
    return JsonResponse({"results": data})

# Create your views here.
