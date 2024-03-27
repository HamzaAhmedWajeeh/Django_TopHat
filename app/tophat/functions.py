from decimal import Decimal


def calculateLoyaltyPoints(order_value=100):
    points_earned = Decimal(order_value) * Decimal('0.1')
    return points_earned