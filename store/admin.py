from typing import Any, List, Tuple
from django.contrib import admin, messages
from django.db.models import Count
from django.db.models.query import QuerySet
from django.utils.html import format_html, urlencode
from django.urls import reverse

from tags.models import TaggedItem
from . import models


class InventoryFilter(admin.SimpleListFilter):
    title = "inventory"
    parameter_name = "inventory"

    def lookups(self, request: Any, model_admin: Any) -> List[Tuple[Any, str]]:
        return [("<10", "Low")]

    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any]:
        if self.value() == "<10":
            return queryset.filter(inventory__lt=10)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ["collection"]
    prepopulated_fields = {"slug": ["title"]}
    search_fields = ["title"]
    actions = ["clear_inventory"]
    list_display = ["title", "unit_price", "inventory_status", "collection_title"]
    list_editable = ["unit_price"]
    list_filter = ["collection", "last_update", InventoryFilter]
    list_per_page = 10
    list_select_related = ["collection"]

    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering="inventory")
    def inventory_status(self, product):
        if product.inventory < 10:
            return f"{product.inventory} Low"
        else:
            return f"{product.inventory} ok"

    @admin.action(description="Clear inventory")
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f"{updated_count} products were seccessfully updated.",
            messages.ERROR,
        )


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "membership", "orders_count"]
    list_editable = ["membership"]
    list_per_page = 10
    list_select_related = ["user"]
    ordering = ["user__first_name", "user__last_name"]
    search_fields = ["first_name__istartswith", "last_name__istartswith"]

    @admin.display(ordering="orders_count")
    def orders_count(self, customer):
        url = (
            reverse("admin:store_order_changelist")
            + "?"
            + urlencode({"customer_id": str(customer.id)})
        )
        return format_html(f"<a href='{url}'>{customer.orders_count} Orders</a>")

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(orders_count=Count("order"))


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["title", "products_count"]
    search_fields = ["title"]

    @admin.display(ordering="products_count")
    def products_count(self, collection):
        url = (
            reverse("admin:store_product_changelist")
            + "?"
            + urlencode({"collection__id": str(collection.id)})
        )
        return format_html(f'<a href="{url}">{collection.products_count}</a>')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_count=Count("products"))


class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ["product"]
    min_num = 1
    max_num = 10
    model = models.OrderItem
    extra = 0


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "placed_at", "customer"]
    inlines = [OrderItemInline]
    autocomplete_fields = ["customer"]
    ordering = ["-placed_at"]
    list_per_page = 10
