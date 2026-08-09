from decimal import Decimal, ROUND_HALF_UP


def stenso_target_price(stenso_public_price, acquisition_floor):
    """
    M99 target = 1.5% below Stenso public price, but never below acquisition floor.
    Values are expected in the same VAT basis/currency before calling this function.
    """
    competitor = Decimal(str(stenso_public_price))
    floor = Decimal(str(acquisition_floor))
    target = competitor * Decimal("0.985")
    result = max(target, floor)
    return result.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
