from .gateway import (
    PagSeguroPayment,
    PaymentMethod,
    CardData,
    PaymentConfig,
    PaymentAmount,
    ChargeConfig,
    CardHolder,
    Customer,
    Address,
    Phone,
    Item,
    AuthenticationMethod,
    _normalize_payment_method
)
from .validators import PaymentValidators
from .enums import PaymentMethod

__version__ = "0.1.0"
__author__ = "Miguel Ilha"
__email__ = "miguel@isla.software"

# Facilita o import das classes principais
__all__ = [
    "PagSeguroPayment",
    "PaymentMethod",
    "CardData",
    "PaymentConfig",
    "PaymentAmount",
    "ChargeConfig",
    "CardHolder",
    "Customer",
    "Address",
    "Phone",
    "Item",
    "AuthenticationMethod",
    "PaymentValidators",
    "_normalize_payment_method"
]
