from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
import os
import requests
from .validators import PaymentValidators
from .enums import PaymentMethod
from datetime import datetime
import uuid
from dotenv import load_dotenv  # Adiciona import do python-dotenv
import logging

# Carrega as variáveis de ambiente
load_dotenv()

@dataclass
class Phone:
    area: str
    number: str
    country: str = "55"
    type: str = "MOBILE"

@dataclass
class CardHolder:
    tax_id: str
    name: str
    email: str

@dataclass
class Address:
    street: str
    number: str
    locality: str
    city: str
    region_code: str
    postal_code: str
    country: str = 'BRA'

@dataclass
class Customer:
    name: str
    email: str
    tax_id: str
    phones: List[Phone]

@dataclass
class Item:
    name: str
    quantity: int
    unit_amount: int

@dataclass
class AuthenticationMethod:
    type: str
    id: str
    cavv: str
    eci: str

@dataclass
class CardData:
    number: str
    exp_month: int
    exp_year: int
    cvv: str
    holder: Optional[CardHolder] = None
    store: Optional[bool] = None
    authentication_method: Optional[AuthenticationMethod] = None

    def __post_init__(self):
        if not (self.exp_month and self.exp_year):
            raise ValueError("Mês e ano de expiração são obrigatórios")

@dataclass
class PaymentAmount:
    value: int
    currency: str = "BRL"

@dataclass
class ChargeConfig:
    reference_id: str
    description: str

@dataclass
class PaymentConfig:
    amount: PaymentAmount
    charge: ChargeConfig
    installments: Optional[int] = None
    capture: Optional[bool] = None
    soft_descriptor: Optional[str] = None

class PagSeguroPayment:
    def __init__(self):
        self.base_url = os.getenv('PAGSEGURO_BASE_URL')
        self.token = os.getenv('PAGSEGURO_TOKEN')
        
        if not self.base_url:
            raise ValueError("PAGSEGURO_BASE_URL não configurado")
        if not self.token:
            raise ValueError("PAGSEGURO_TOKEN não configurado")

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def _build_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def _build_card_payment(self, payment_method: PaymentMethod, card_data: CardData, payment_config: PaymentConfig) -> Dict:
        self.logger.debug(f"Construindo dados de pagamento para método: {payment_method}")
            
        # Log seguro (mascarado)
        self.logger.debug(f"Card number: ****{card_data.number[-4:]}")
        self.logger.debug("Security code: ***")
        
        # Dados reais para o payload
        payment_method_data = {
            "type": payment_method.value,
            "card": {
                "number": card_data.number,  # Número real do cartão
                "exp_month": card_data.exp_month,
                "exp_year": card_data.exp_year,
                "security_code": card_data.cvv,  # CVV real
                "holder": asdict(card_data.holder)
            }
        }

        if payment_method == PaymentMethod.CREDIT_CARD:
            payment_method_data.update({
                "installments": payment_config.installments or 1,
                "capture": payment_config.capture or True,
                "soft_descriptor": payment_config.soft_descriptor
            })
        elif payment_method == PaymentMethod.DEBIT_CARD and card_data.authentication_method:
            self.logger.debug("Adicionando dados de autenticação 3DS ao payload")
            self.logger.debug(f"Authentication data: {card_data.authentication_method}")
            payment_method_data["authentication_method"] = card_data.authentication_method

        # Log seguro do payload final (mascarando dados sensíveis)
        safe_payload = {**payment_method_data}
        if 'card' in safe_payload:
            safe_payload['card'] = {
                **safe_payload['card'],
                'number': f"****{card_data.number[-4:]}",
                'security_code': '***'
            }
        self.logger.debug(f"Payload final do pagamento: {safe_payload}")
        
        return payment_method_data

    def _normalize_payment_method(self, method: str) -> PaymentMethod:
        """Normaliza o método de pagamento para o enum correto"""
        method = str(method).lower().strip()
        
        credit_variations = [
            'credit', 'credito', 'crédito', 'crédit',
            'cartao de credito', 'cartão de crédito', 
            'cartao credito', 'cartão crédito',
            'credit card', 'creditcard',
            'cc', 'cartão cred', 'cartao cred'
        ]
        
        debit_variations = [
            'debit', 'debito', 'débito', 'débit',
            'cartao de debito', 'cartão de débito',
            'cartao debito', 'cartão débito',
            'debit card', 'debitcard',
            'dc', 'cartão deb', 'cartao deb'
        ]
        
        pix_variations = ['pix', 'PIX']
        
        if method in credit_variations:
            return PaymentMethod.CREDIT_CARD
        elif method in debit_variations:
            return PaymentMethod.DEBIT_CARD
        elif method in pix_variations:
            return PaymentMethod.PIX
        else:
            raise ValueError(f"Método de pagamento '{method}' não suportado")

    def process_payment(self, payment_data: dict):
        """
        Processa um pagamento usando o PagBank/PagSeguro
        """
        try:
            # Usa a função de normalização
            payment_method = self._normalize_payment_method(payment_data.get('payment_method'))
            
            customer = Customer(
                name=payment_data['customer']['name'],
                email=payment_data['customer']['email'],
                tax_id=payment_data['customer']['tax_id'],
                phones=payment_data['customer'].get('phones', [])
            )
            
            address = Address(
                street=payment_data['shipping']['address']['street'],
                number=payment_data['shipping']['address']['number'],
                locality=payment_data['shipping']['address']['locality'],
                city=payment_data['shipping']['address']['city'],
                region_code=payment_data['shipping']['address']['region_code'],
                country=payment_data['shipping']['address'].get('country', 'BRA'),
                postal_code=payment_data['shipping']['address']['postal_code']
            )

            # Criar item baseado no amount
            items = [
                Item(
                    name="Pagamento",
                    quantity=1,
                    unit_amount=int(payment_data['amount'] * 100)  # converter para centavos
                )
            ]

            payment_config = PaymentConfig(
                amount=PaymentAmount(value=int(payment_data['amount'] * 100)),  # converter para centavos
                charge=ChargeConfig(
                    reference_id=str(uuid.uuid4()),
                    description='Pagamento via PagBank'
                ),
                installments=payment_data.get('installments', 1)
            )
            
            card_holder = CardHolder(
                name=payment_data['card_data']['owner'],
                tax_id=payment_data['customer']['tax_id'],
                email=payment_data['customer']['email']
            )
            
            card_data = CardData(
                number=payment_data['card_data']['number'],
                cvv=payment_data['card_data']['cvv'],
                exp_month=payment_data['card_data']['exp_month'],
                exp_year=payment_data['card_data']['exp_year'],
                holder=card_holder,
                authentication_method=payment_data['card_data']['authentication_method']
            )
            
            return self.create_payment(
                customer=customer,
                address=address,
                items=items,
                payment_method=payment_method,
                payment_config=payment_config,
                card_data=card_data
            )
            
        except Exception as e:
            raise ValueError(f"Erro ao processar pagamento: {str(e)}")

    def create_payment(self, customer: Customer, address: Address, items: List[Item],
                      payment_method: PaymentMethod, payment_config: PaymentConfig,
                      card_data: Optional[CardData] = None) -> Dict:
        self.logger.info("Iniciando criação de pagamento no PagSeguro")
        PaymentValidators.validate_customer_data(asdict(customer))
        PaymentValidators.validate_address(asdict(address))
        PaymentValidators.validate_payment_config(asdict(payment_config))
        
        if card_data and payment_method in [PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD]:
            PaymentValidators.validate_card_data(asdict(card_data))
            
            if payment_method == PaymentMethod.CREDIT_CARD and payment_config.installments:
                PaymentValidators.validate_installments(payment_config.installments)
        
        if payment_method == PaymentMethod.PIX:
            pix_expiration = os.getenv('PIX_EXPIRATION_DATE')
            PaymentValidators.validate_pix_expiration(pix_expiration)
        
        base_payment_data = {
            "customer": asdict(customer),
            "shipping": {
                "address": asdict(address)
            },
            "items": [asdict(item) for item in items],
            "reference_id": payment_config.charge.reference_id,
        }

        if payment_method == PaymentMethod.PIX:
            pix_expiration = os.getenv('PIX_EXPIRATION_DATE')
            if not pix_expiration:
                raise ValueError("PIX_EXPIRATION_DATE não configurado")
                
            base_payment_data["qr_codes"] = [{
                "amount": {
                    "value": payment_config.amount.value
                },
                "expiration_date": pix_expiration
            }]
        else:
            base_payment_data["charges"] = [{
                "reference_id": payment_config.charge.reference_id,
                "description": payment_config.charge.description,
                "amount": {
                    "value": payment_config.amount.value,
                    "currency": payment_config.amount.currency
                },
                "payment_method": self._build_card_payment(payment_method, card_data, payment_config)
            }]

        if payment_method == PaymentMethod.DEBIT_CARD:
            # Garante que o payment_method_data está no nível correto do JSON
            base_payment_data["charges"][0]["payment_method"] = self._build_card_payment(
                payment_method, card_data, payment_config
            )

        response = requests.post(
            f"{self.base_url}/orders",
            json=base_payment_data,
            headers=self._build_headers()
        )

        if response.status_code not in (200, 201):
            raise Exception(f"Erro ao criar pagamento: {response.text}")

        return response.json()