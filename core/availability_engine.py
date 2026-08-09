from enum import Enum
class AvailabilityStatus(str, Enum):
    OWN_STOCK="OWN_STOCK"
    SUPPLIER_STOCK="SUPPLIER_STOCK"
    OUT_OF_STOCK="OUT_OF_STOCK"

def decide_availability(own_stock, supplier_stock):
    if own_stock > 0:
        return AvailabilityStatus.OWN_STOCK, "В наличност", True
    if supplier_stock > 0:
        return AvailabilityStatus.SUPPLIER_STOCK, "Наличен при доставчик", True
    return AvailabilityStatus.OUT_OF_STOCK, "Изчерпан", False
