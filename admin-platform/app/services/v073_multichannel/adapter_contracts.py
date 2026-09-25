from .channel_registry import CHANNELS
class WriteBlocked(RuntimeError):pass
def contracts():return {c["channel_id"]:{"platform":c["platform"],"mutation_allowed":False,"mode":"READ_ONLY_PREFLIGHT","capabilities":["connectivity","product_lookup_by_reference","duplicate_lookup","category_readback","currency_readback","tax_readback"]} for c in CHANNELS}
def blocked_write(*a,**k):raise WriteBlocked("WRITE_BLOCKED_R730_R22")
