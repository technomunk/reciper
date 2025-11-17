def item_rate(item: str, rate: float = 1) -> str:
    rate = int(rate) if rate.is_integer() else rate
    return f"{rate}x {item.title()}"
