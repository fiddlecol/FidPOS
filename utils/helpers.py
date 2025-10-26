def format_currency(amount):
    """Format a number into Kenyan Shillings currency format."""
    try:
        return f"KSh {float(amount):,.2f}"
    except (ValueError, TypeError):
        return "KSh 0.00"

# 