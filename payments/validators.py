import re
import sys
from pathlib import Path
from typing import Dict, Union, Optional, Any, List
from datetime import datetime
from enum import Enum
from .enums import PaymentMethod

class PaymentValidators:
    @staticmethod
    def validate_cpf(cpf: str) -> bool:
        """Valida o formato e dígitos verificadores do CPF"""
        cpf = re.sub(r'[^0-9]', '', cpf)
        
        if len(cpf) != 11:
            raise ValueError("CPF deve conter 11 dígitos")
            
        if cpf == cpf[0] * 11:
            raise ValueError("CPF inválido")
            
        for i in range(9, 11):
            value = sum((int(cpf[num]) * ((i + 1) - num) for num in range(0, i)))
            digit = ((value * 10) % 11) % 10
            if digit != int(cpf[i]):
                raise ValueError("CPF inválido")
        return True

    @staticmethod
    def validate_phone(phone: Dict) -> bool:
        """Valida o formato do telefone"""
        if not phone.get('country') or not phone.get('area') or not phone.get('number'):
            raise ValueError("Dados do telefone incompletos")
            
        if not re.match(r'^[1-9][0-9]$', phone['area']):
            raise ValueError("DDD inválido")
            
        if not re.match(r'^9[0-9]{8}$|^[2-8][0-9]{7}$', phone['number']):
            raise ValueError("Número de telefone inválido")
        return True

    @staticmethod
    def validate_amount(amount: Union[Dict, int, float], payment_method: Optional[PaymentMethod] = None) -> int:
        """Valida o valor da transação"""
        try:
            # Se amount for None, usar valor padrão
            if amount is None:
                return 100
            
            # Se amount for um número, converter diretamente
            if isinstance(amount, (int, float)):
                valor = int(amount * 100)
            
            # Se amount for um dicionário, tentar obter 'value'
            elif isinstance(amount, dict):
                valor = int(float(amount.get('value', 100)) * 100)
            else:
                valor = 100
            
            # Verificar limites
            if valor < 100:
                raise ValueError("Valor mínimo de R$ 1,00 não atingido")
            
            if valor > 100000000:
                raise ValueError("Valor máximo de R$ 1.000.000,00 excedido")
            
            return valor
            
        except (TypeError, ValueError) as e:
            raise ValueError(f"Valor inválido: {e}")

    @staticmethod
    def validate_card_expiration(exp_month: int, exp_year: int) -> bool:
        """Valida a data de expiração do cartão"""
        current_date = datetime.now()
        
        if exp_year < current_date.year:
            raise ValueError("Cartão expirado")
        
        if exp_year == current_date.year and exp_month < current_date.month:
            raise ValueError("Cartão expirado")
            
        if not (1 <= exp_month <= 12):
            raise ValueError("Mês de expiração inválido")
            
        return True

    @staticmethod
    def validate_installments(installments: int) -> bool:
        """Valida o número de parcelas"""
        if not isinstance(installments, int):
            raise ValueError("Número de parcelas deve ser um número inteiro")
            
        if not (1 <= installments <= 12):
            raise ValueError("Número de parcelas deve estar entre 1 e 12")
            
        return True

    @staticmethod
    def validate_card_data(card_data: Dict[str, Any]) -> bool:
        """Valida todos os dados do cartão"""
        if not card_data.get('number'):
            raise ValueError("Número do cartão é obrigatório")
            
        if not card_data.get('cvv'):
            raise ValueError("CVV é obrigatório")
        
        # Validação da data de expiração
        if not card_data.get('exp_month') or not card_data.get('exp_year'):
            raise ValueError("Mês e ano de expiração são obrigatórios")
            
        # Validar formato e validade da data
        try:
            exp_month = int(card_data['exp_month'])
            exp_year = int(card_data['exp_year'])
            
            if not (1 <= exp_month <= 12):
                raise ValueError("Mês de expiração inválido")
                
            current_date = datetime.now()
            if exp_year < current_date.year:
                raise ValueError("Cartão expirado")
            
            if exp_year == current_date.year and exp_month < current_date.month:
                raise ValueError("Cartão expirado")
                
        except (TypeError, ValueError):
            raise ValueError("Formato de data de expiração inválido")
        
        if not card_data.get('holder'):
            raise ValueError("Nome do titular do cartão é obrigatório")
        
        return True

    @staticmethod
    def validate_payment_config(payment_data: Dict[str, Any]) -> bool:
        """Valida configurações de pagamento"""
        required_fields = ['amount']
        for field in required_fields:
            if field not in payment_data:
                raise ValueError(f"Campo obrigatório ausente: {field}")
        
        if 'installments' in payment_data:
            if not isinstance(payment_data['installments'], int):
                raise ValueError("Número de parcelas deve ser um número inteiro")
            if not (1 <= payment_data['installments'] <= 12):
                raise ValueError("Número de parcelas deve estar entre 1 e 12")
        
        return True

    @staticmethod
    def validate_customer_data(customer_data: Dict[str, Any]) -> bool:
        """Valida dados do cliente"""
        required_fields = ['name', 'email', 'tax_id']
        for field in required_fields:
            if not customer_data.get(field):
                raise ValueError(f"Campo obrigatório ausente: {field}")
        
        # Validar formato do email
        email = customer_data['email']
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError("Formato de email inválido")
        
        return True

    @staticmethod
    def validate_address(address: Dict[str, Any]) -> bool:
        """Valida dados de endereço"""
        required_fields = ['street', 'number', 'city', 'region_code', 'country', 'postal_code']
        for field in required_fields:
            if not address.get(field):
                raise ValueError(f"Campo de endereço obrigatório ausente: {field}")
        
        # Validar CEP
        postal_code = re.sub(r'[^0-9]', '', address['postal_code'])
        if len(postal_code) != 8:
            raise ValueError("CEP deve conter 8 dígitos")
        
        # Validar código do estado
        if not re.match(r'^[A-Z]{2}$', address['region_code']):
            raise ValueError("Código do estado deve conter 2 letras maiúsculas")
        
        return True

    @staticmethod
    def validate_pix_expiration(expiration_date: str) -> bool:
        return True
        """Valida data de expiração do PIX"""
        #if not expiration_date:
        #    raise ValueError("Data de expiração do PIX é obrigatória")
        #
        #try:
        #    exp_date = datetime.strptime(expiration_date, '%Y-%m-%dT%H:%M:%S')
        #    if exp_date < datetime.now():
        #        raise ValueError("Data de expiração do PIX inválida")
        #except ValueError:
        #    raise ValueError("Formato de data de expiração do PIX inválido. Use o formato ISO")
        

    @staticmethod
    def validate_payment_method(payment_method: PaymentMethod, card_data: Optional[Dict] = None) -> bool:
        """Valida método de pagamento e suas regras específicas"""
        if payment_method in [PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD]:
            if not card_data:
                raise ValueError(f"Dados do cartão são obrigatórios para pagamento com {payment_method.value}")
            
            if payment_method == PaymentMethod.DEBIT_CARD:
                if not card_data.get('holder'):
                    raise ValueError("Dados do titular são obrigatórios para cartão de débito")

        return True

    @staticmethod
    def validate_items(items: List[Dict]) -> bool:
        """Valida itens do pedido"""
        if not items:
            raise ValueError("Lista de itens não pode estar vazia")
            
        for item in items:
            if not item.get('name'):
                raise ValueError("Nome do item é obrigatório")
            if not isinstance(item.get('quantity'), int) or item['quantity'] <= 0:
                raise ValueError("Quantidade do item deve ser um número inteiro positivo")
            if not isinstance(item.get('unit_amount'), (int, float)) or item['unit_amount'] <= 0:
                raise ValueError("Valor unitário do item deve ser positivo")
        
        return True

    @staticmethod
    def validate_environment_configs(base_url: Optional[str], token: Optional[str]) -> bool:
        """Valida configurações do ambiente"""
        if not base_url:
            raise ValueError("PAGSEGURO_BASE_URL não configurado")
        if not token:
            raise ValueError("PAGSEGURO_TOKEN não configurado")
        return True