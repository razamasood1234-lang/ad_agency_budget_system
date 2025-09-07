__all__ = ['check_budgets_and_schedules_task', 'reset_daily_spend_task', 'reset_monthly_spend_task']

from celery import shared_task
from django.utils import timezone
from datetime import datetime, time, date
from django.db.models import Sum, F
from .models import Campaign, Brand, DaypartingSchedule

@shared_task
def check_budgets_and_schedules_task():
    """
    A periodic task to check ALL campaigns against their
    brand budgets and dayparting schedules.
    Should run every 5-10 minutes.
    """
    # 1. Get ALL campaigns, not just active ones
    all_campaigns = Campaign.objects.all().select_related('brand')
    
    for campaign in all_campaigns:
        should_be_active = True
        pause_reason = None

        # 2. Check Dayparting Schedule
        schedule = getattr(campaign, 'schedule', None)
        if schedule:
            now = timezone.now()
            current_time = now.time()
            
            # Check if current time is outside scheduled hours
            if current_time < schedule.start_time or current_time > schedule.end_time:
                should_be_active = False
                pause_reason = "Outside scheduled hours"

        # 3. Check Brand Budgets (only if not already paused by schedule)
        if should_be_active:
            brand = campaign.brand
            if brand.daily_spend >= brand.daily_budget:
                should_be_active = False
                pause_reason = "Daily budget exceeded"
            elif brand.monthly_spend >= brand.monthly_budget:
                should_be_active = False
                pause_reason = "Monthly budget exceeded"

        # 4. Determine if we need to change the campaign status
        current_status = campaign.is_active
        proposed_status = should_be_active
        
        if current_status != proposed_status:
            # Status needs to be changed
            if proposed_status:
                # Reactivate the campaign
                campaign.is_active = True
                campaign.paused_because_of_budget = False
                campaign.save()
                print(f"Reactivated campaign '{campaign.name}'. Reason: Conditions now met")
            else:
                # Pause the campaign
                campaign.is_active = False
                campaign.paused_because_of_budget = ("budget" in pause_reason.lower() if pause_reason else False)
                campaign.save()
                print(f"Paused campaign '{campaign.name}'. Reason: {pause_reason}")
        else:
            # Status doesn't need to change, but update pause reason if needed
            if not proposed_status and campaign.paused_because_of_budget and pause_reason and ("budget" not in pause_reason.lower()):
                campaign.paused_because_of_budget = False
                campaign.save()

@shared_task
def reset_daily_spend_task():
    """
    Reset daily spend for all brands and reactivate eligible campaigns.
    Should run daily at midnight.
    """
    # 1. Reset all daily spends to zero
    Brand.objects.update(daily_spend=0.00)
    
    # 2. Reactivate campaigns paused due to daily budget
    campaigns_to_reactivate = Campaign.objects.filter(
        is_active=False,
        paused_because_of_budget=True
    ).select_related('brand')
    
    for campaign in campaigns_to_reactivate:
        # Only reactivate if monthly budget is still available
        if campaign.brand.monthly_spend < campaign.brand.monthly_budget:
            campaign.is_active = True
            campaign.paused_because_of_budget = False
            campaign.save()
            print(f"Reactivated campaign '{campaign.name}' after daily reset")

@shared_task
def reset_monthly_spend_task():
    """
    Reset monthly spend for all brands and reactivate eligible campaigns.
    Should run on the first day of each month.
    """
    # 1. Reset all monthly spends to zero
    today = timezone.now().date()
    if today.day == 1:  # Only reset on the first day of the month
        Brand.objects.update(monthly_spend=0.00)
        
        # 2. Reactivate all campaigns paused due to budget
        campaigns_to_reactivate = Campaign.objects.filter(
            is_active=False,
            paused_because_of_budget=True
        )
        
        for campaign in campaigns_to_reactivate:
            campaign.is_active = True
            campaign.paused_because_of_budget = False
            campaign.save()
            print(f"Reactivated campaign '{campaign.name}' after monthly reset")
    else:
        print("Not the first day of the month. Monthly reset skipped.")