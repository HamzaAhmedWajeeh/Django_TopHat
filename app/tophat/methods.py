import hashlib


def calculate_total(item_price, quantity):
    return item_price * quantity

def generate_redemption_id(user_id, order_date, order_time):

    unique_string = f"{user_id}-{order_date}-{order_time}"
    redemption_id = unique_string.replace('-', '').replace(':', '')

    return redemption_id