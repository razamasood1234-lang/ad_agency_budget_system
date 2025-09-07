from django.contrib import admin
from .models import Brand, Campaign, DaypartingSchedule, SpendLog

# Register your models here.

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Admin configuration for the Brand model."""
    list_display = ('name', 'daily_budget', 'monthly_budget', 'daily_spend', 'monthly_spend')
    list_filter = ('name',)
    search_fields = ('name',)
    # This defines the order of fields in the detail form
    fieldsets = (
        (None, {
            'fields': ('name', 'daily_budget', 'monthly_budget')
        }),
        ('Current Spend (Auto-updated)', {
            'fields': ('daily_spend', 'monthly_spend'),
            'classes': ('collapse',) # This makes this section collapsible
        }),
    )

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    """Admin configuration for the Campaign model."""
    list_display = ('name', 'brand', 'is_active', 'paused_because_of_budget', 'total_spend')
    list_filter = ('brand', 'is_active', 'paused_because_of_budget')
    search_fields = ('name', 'brand__name') # Allows searching by campaign name OR brand name
    list_editable = ('is_active',) # Lets you toggle is_active right from the list view
    # Defines the fields shown on the detail form
    fields = ('brand', 'name', 'is_active', 'paused_because_of_budget', 'total_spend')

@admin.register(DaypartingSchedule)
class DaypartingScheduleAdmin(admin.ModelAdmin):
    """Admin configuration for the DaypartingSchedule model."""
    list_display = ('campaign', 'start_time', 'end_time')
    list_filter = ('start_time', 'end_time')
    # The search will show results based on the campaign's __str__ representation
    search_fields = ('campaign__name',)

@admin.register(SpendLog)
class SpendLogAdmin(admin.ModelAdmin):
    """Admin configuration for the SpendLog model."""
    list_display = ('campaign', 'amount', 'timestamp')
    list_filter = ('timestamp', 'campaign__brand')
    search_fields = ('campaign__name',)
    # Makes the timestamp field read-only since it's auto-set
    readonly_fields = ('timestamp',)
    # This is useful to prevent creating fake spend logs in the admin for testing
    # For actual spending, we will use a management command or a Celery task.