"""Thin, defensive wrappers around the supplied capstone tools."""
import sys
from pathlib import Path
from .config import DATASET_DIR

if str(DATASET_DIR) not in sys.path: sys.path.insert(0,str(DATASET_DIR))
try:
    from tools import lookup_order, create_ticket
except Exception:
    lookup_order = create_ticket = None

def order_lookup(order_id, verification_value=None):
    if lookup_order is None:
        return {"error": "Dataset tools unavailable. Check DATASET_DIR in .env."}
    return lookup_order(str(order_id), verification_value=verification_value)

def ticket_create(summary, order_id=None, reason=None, intent=None):
    if create_ticket is None:
        return {"created": False, "error": "Dataset tools unavailable. Check DATASET_DIR in .env."}
    return create_ticket(summary=summary, order_id=order_id, reason=reason, intent=intent)
