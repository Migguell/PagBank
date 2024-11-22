import os
from dotenv import load_dotenv
from gateway import (
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
    AuthenticationMethod
)

load_dotenv()

payment_gateway = PagSeguroPayment()

credit_card = CardData(
    number=os.getenv('CREDIT_CARD_NUMBER'),
    exp_month=int(os.getenv('CREDIT_CARD_EXP_MONTH')),
    exp_year=int(os.getenv('CREDIT_CARD_EXP_YEAR')),
    security_code=os.getenv('CREDIT_CARD_SECURITY_CODE'),
    store=os.getenv('CREDIT_CARD_STORE', 'True').lower() == 'true',
    holder=CardHolder(
        tax_id=os.getenv('CREDIT_CARD_HOLDER_TAX_ID'),
        name=os.getenv('CREDIT_CARD_HOLDER_NAME'),
        email=os.getenv('CREDIT_CARD_HOLDER_EMAIL')
    )
)

credit_config = PaymentConfig(
    amount=PaymentAmount(
        value=int(os.getenv('CREDIT_PAYMENT_AMOUNT')),
        currency=os.getenv('PAYMENT_CURRENCY')
    ),
    charge=ChargeConfig(
        reference_id=os.getenv('CREDIT_REFERENCE_ID'),
        description=os.getenv('CREDIT_DESCRIPTION')
    ),
    installments=int(os.getenv('CREDIT_INSTALLMENTS')),
    capture=os.getenv('CREDIT_CAPTURE', 'True').lower() == 'true',
    soft_descriptor=os.getenv('CREDIT_SOFT_DESCRIPTOR')
)

auth_method = AuthenticationMethod(
    type=os.getenv('AUTH_METHOD_TYPE'),
    id=os.getenv('AUTH_METHOD_ID'),
    cavv=os.getenv('AUTH_METHOD_CAVV'),
    eci=os.getenv('AUTH_METHOD_ECI')
)

debit_card = CardData(
    number=os.getenv('DEBIT_CARD_NUMBER'),
    exp_month=int(os.getenv('DEBIT_CARD_EXP_MONTH')),
    exp_year=int(os.getenv('DEBIT_CARD_EXP_YEAR')),
    security_code=os.getenv('DEBIT_CARD_SECURITY_CODE'),
    holder=CardHolder(
        tax_id=os.getenv('DEBIT_CARD_HOLDER_TAX_ID'),
        name=os.getenv('DEBIT_CARD_HOLDER_NAME'),
        email=os.getenv('DEBIT_CARD_HOLDER_EMAIL')
    ),
    authentication_method=auth_method
)

debit_config = PaymentConfig(
    amount=PaymentAmount(
        value=int(os.getenv('DEBIT_PAYMENT_AMOUNT')),
        currency=os.getenv('PAYMENT_CURRENCY')
    ),
    charge=ChargeConfig(
        reference_id=os.getenv('DEBIT_REFERENCE_ID'),
        description=os.getenv('DEBIT_DESCRIPTION')
    )
)

pix_config = PaymentConfig(
    amount=PaymentAmount(
        value=int(os.getenv('PIX_PAYMENT_AMOUNT')),
        currency=os.getenv('PAYMENT_CURRENCY')
    ),
    charge=ChargeConfig(
        reference_id=os.getenv('PIX_REFERENCE_ID'),
        description=os.getenv('PIX_DESCRIPTION')
    )
)

customer = Customer(
    name=os.getenv('CUSTOMER_NAME'),
    email=os.getenv('CUSTOMER_EMAIL'),
    tax_id=os.getenv('CUSTOMER_TAX_ID'),
    phones=[Phone(
        country=os.getenv('CUSTOMER_PHONE_COUNTRY'),
        area=os.getenv('CUSTOMER_PHONE_AREA'),
        number=os.getenv('CUSTOMER_PHONE_NUMBER'),
        type=os.getenv('CUSTOMER_PHONE_TYPE', 'MOBILE')
    )]
)

address = Address(
    street=os.getenv('ADDRESS_STREET'),
    number=os.getenv('ADDRESS_NUMBER'),
    locality=os.getenv('ADDRESS_LOCALITY'),
    city=os.getenv('ADDRESS_CITY'),
    region_code=os.getenv('ADDRESS_REGION_CODE'),
    country=os.getenv('ADDRESS_COUNTRY'),
    postal_code=os.getenv('ADDRESS_POSTAL_CODE')
)

items = [
    Item(
        name=os.getenv('ITEM_NAME'),
        quantity=int(os.getenv('ITEM_QUANTITY')),
        unit_amount=int(os.getenv('ITEM_UNIT_AMOUNT'))
    )
]

payment_method = os.getenv('PAYMENT_METHOD', 'CREDIT_CARD')

if payment_method == 'CREDIT_CARD':
    payment = payment_gateway.create_payment(
        customer=customer,
        address=address,
        items=items,
        payment_method=PaymentMethod.CREDIT_CARD,
        payment_config=credit_config,
        card_data=credit_card
    )
elif payment_method == 'DEBIT_CARD':
    payment = payment_gateway.create_payment(
        customer=customer,
        address=address,
        items=items,
        payment_method=PaymentMethod.DEBIT_CARD,
        payment_config=debit_config,
        card_data=debit_card
    )
elif payment_method == 'PIX':
    payment = payment_gateway.create_payment(
        customer=customer,
        address=address,
        items=items,
        payment_method=PaymentMethod.PIX,
        payment_config=pix_config,
        card_data=None
    )

print("\n=== Payment Response ===")
print(f"Status: Success")
print("\nPayment Details:")
for key, value in payment.items():
    if isinstance(value, dict):
        print(f"\n{key}:")
        for k, v in value.items():
            print(f"  {k}: {v}")
    else:
        print(f"{key}: {value}") 