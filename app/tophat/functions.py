from decimal import Decimal
from core.models import LoyaltyPointsPercentage


def calculateLoyaltyPoints(order_value):
    loyalty_points_percentage = LoyaltyPointsPercentage.objects.first()

    if loyalty_points_percentage:
        points_percentage = loyalty_points_percentage.percentage
    else:
        # If no percentage is found, default to 10%
        points_percentage = Decimal('0.1')

    points_earned = Decimal(order_value) * Decimal(points_percentage)

    return points_earned