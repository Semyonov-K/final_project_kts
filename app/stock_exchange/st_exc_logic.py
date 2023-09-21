import random

async def calculate_price_change(price, minran, maxran):
    price_change_percent = (random.randint(minran, maxran) / 100)
    price_change = price - (price_change_percent * price)
    return price_change
