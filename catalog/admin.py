from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('sku','name','category','price','stock_qty','status','updated_at')
    list_filter = ('category','status')
    search_fields = ('sku','name','category')
    ordering = ('sku',)
    list_per_page = 50

    actions = ['make_active','make_inactive']

    def make_active(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f"{updated} products marked active.")
    make_active.short_description = "Mark selected products as active"

    def make_inactive(self, request, queryset):
        updated = queryset.update(status='inactive')
        self.message_user(request, f"{updated} products marked inactive.")
    make_inactive.short_description = "Mark selected products as inactive"
