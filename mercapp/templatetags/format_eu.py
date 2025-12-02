from django import template
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

register = template.Library()

@register.filter(is_safe=True)
def format_euro(value):
    """Format a number in European style: thousands separator '.' and no decimals.

    Examples:
    - 2800.00 -> '2.800'
    - 1234567.89 -> '1.234.568' (rounded)
    If value cannot be converted, return it unchanged.
    """
    if value is None:
        return ''
    try:
        d = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return value
    # Round to nearest integer
    d = d.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    try:
        n = int(d)
    except (ValueError, OverflowError):
        return str(d)
    # Use English thousands separator and replace comma with dot
    s = f"{n:,}"
    return s.replace(',', '.')
