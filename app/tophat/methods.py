def calculate_total(item_price, quantity):
    return item_price * quantity

def generate_redemption_id(user_id, order_date, order_time):

    unique_string = f"{user_id}-{order_date}-{order_time}"
    redemption_id = unique_string.replace('-', '').replace(':', '')

    return redemption_id

def calculate_total_price(base_price, quantity, extras_prices, kitchen_notes_prices):
    total_price = base_price * quantity

    for price in extras_prices.values():
        total_price += price

    for price in kitchen_notes_prices.values():
        total_price += price

    return total_price