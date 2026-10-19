from django.contrib import admin


from . models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["student", "course", "amount", "status"]
    list_filter = ["student"]
    search_fields = ["student__email"]
    readonly_fields = [
        "student",
        "course",
        "amount",
        "currency",
        "status",
        "stripe_session_id",
        "stripe_event_id",
    ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False