from django.core.management.base import BaseCommand
from budget.models import Campaign, SpendLog, Brand
from decimal import Decimal
import sys

class Command(BaseCommand):
    help = 'Simulate an ad spend for a specific campaign'

    def add_arguments(self, parser):
        parser.add_argument(
            'campaign_id',
            type=int,
            help='The ID of the campaign to add spend to'
        )
        parser.add_argument(
            'amount',
            type=Decimal,
            help='The amount to spend (e.g., 15.50)'
        )

    def handle(self, *args, **options):
        campaign_id = options['campaign_id']
        amount = options['amount']

        try:
            # 1. Get the campaign and its brand
            campaign = Campaign.objects.get(id=campaign_id)
            brand = campaign.brand
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Campaign: {campaign.name} (Brand: {brand.name})"
                )
            )
            self.stdout.write(
                f"Current spend - Campaign: ${campaign.total_spend}, "
                f"Brand Daily: ${brand.daily_spend}/{brand.daily_budget}, "
                f"Brand Monthly: ${brand.monthly_spend}/{brand.monthly_budget}"
            )

            # 2. Create the SpendLog (this is the core transaction)
            spend_log = SpendLog.objects.create(
                campaign=campaign,
                amount=amount
            )

            # 3. Update the running totals
            campaign.total_spend += amount
            campaign.save()

            brand.daily_spend += amount
            brand.monthly_spend += amount
            brand.save()

            # 4. Show success message with updated totals
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully logged ${amount} spend for '{campaign.name}'"
                )
            )
            self.stdout.write(
                f"Updated spend - Campaign: ${campaign.total_spend}, "
                f"Brand Daily: ${brand.daily_spend}/{brand.daily_budget}, "
                f"Brand Monthly: ${brand.monthly_spend}/{brand.monthly_budget}"
            )

            # 5. Warn if budgets are exceeded
            if brand.daily_spend >= brand.daily_budget:
                self.stdout.write(
                    self.style.WARNING(
                        "⚠️  Daily budget exceeded! Campaign should be paused soon."
                    )
                )
            if brand.monthly_spend >= brand.monthly_budget:
                self.stdout.write(
                    self.style.WARNING(
                        "⚠️  Monthly budget exceeded! Campaign should be paused soon."
                    )
                )

        except Campaign.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"Campaign with ID {campaign_id} does not exist.")
            )
            sys.exit(1)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"An error occurred: {str(e)}")
            )
            sys.exit(1)