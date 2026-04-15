from django.db import models


class FinancialStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pendente'
    PAID = 'PAID', 'Pago'
    PARTIAL = 'PARTIAL', 'Parcial'
    OVERDUE = 'OVERDUE', 'Atrasado'
    CANCELED = 'CANCELED', 'Cancelado'


class PaymentType(models.TextChoices):
    SESSION = 'SESSION', 'Sessão'
    PACKAGE = 'PACKAGE', 'Pacote'
    MEMBERSHIP = 'MEMBERSHIP', 'Mensalidade'


class TransactionType(models.TextChoices):
    INCOME = 'IN', 'Receita'
    EXPENSE = 'OUT', 'Despesa'


class PaymentMethod(models.TextChoices):
    CASH = 'CASH', 'Dinheiro'
    PIX = 'PIX', 'Pix'
    CREDIT_CARD = 'CREDIT_CARD', 'Cartão de Crédito'
    DEBIT_CARD = 'DEBIT_CARD', 'Cartão de Débito'
    TRANSFER = 'TRANSFER', 'Transferência/Boleto'


class FinancialOrigin(models.TextChoices):
    SUBSCRIPTION = 'SUBSCRIPTION', 'Mensalidade/Contrato'
    PACKAGE = 'PACKAGE', 'Venda de Pacote'
    SINGLE_SESSION = 'SINGLE_SESSION', 'Aula Avulsa'
    OTHER = 'OTHER', 'Outros'


class CashStatus(models.TextChoices):
    OPEN = 'OPEN', 'Aberto'
    CLOSED = 'CLOSED', 'Fechado'