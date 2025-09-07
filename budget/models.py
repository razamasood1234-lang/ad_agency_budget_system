from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Brand(models.Model):
    """Represents an advertiser brand with daily and monthly budgets."""
    name = models.CharField(max_length=255, unique=True)
    daily_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    monthly_budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    # These fields are updated whenever a SpendLog is created
    daily_spend = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    monthly_spend = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    def __str__(self) -> str:
        return f"{self.name} (Daily: ${self.daily_spend}/${self.daily_budget})"

    class Meta:
        ordering = ['name']

class Campaign(models.Model):
    """Represents an individual advertising campaign under a Brand."""
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE, # If a brand is deleted, delete its campaigns
        related_name='campaigns' # Allows us to use brand.campaigns.all()
    )
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(
        default=True,
        help_text="Manual control to activate/deactivate the campaign."
    )
    paused_because_of_budget = models.BooleanField(
        default=False,
        help_text="Flag indicating if the campaign was auto-paused due to budget limits."
    )
    total_spend = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    def __str__(self) -> str:
        return f"{self.brand.name} - {self.name}"

    class Meta:
        # A brand cannot have two campaigns with the same name
        unique_together = ['brand', 'name']
        ordering = ['brand__name', 'name']

class DaypartingSchedule(models.Model):
    """Defines the daily time window when a campaign is allowed to run."""
    campaign = models.OneToOneField(
        Campaign,
        on_delete=models.CASCADE, # If the campaign is deleted, delete its schedule
        related_name='schedule' # Allows us to use campaign.schedule
    )
    start_time = models.TimeField(
        help_text="The time of day the campaign should start (e.g., 09:00)."
    )
    end_time = models.TimeField(
        help_text="The time of day the campaign should end (e.g., 17:00)."
    )

    def __str__(self) -> str:
        return f"Schedule for {self.campaign.name} ({self.start_time} - {self.end_time})"

class SpendLog(models.Model):
    """A log of every individual spend event for a campaign."""
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE, # If campaign is deleted, delete its spend logs
        related_name='spend_logs' # Allows us to use campaign.spend_logs.all()
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))] # Must spend at least 1 cent
    )
    timestamp = models.DateTimeField(auto_now_add=True) # Automatically set on creation

    def __str__(self) -> str:
        return f"${self.amount} spent on {self.campaign.name} at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp'] # Show most recent spends first