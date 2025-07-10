# financije/serializers.py

from rest_framework import serializers

from client_app.models import ClientSupplier

from .models import FinancialDetails  # Dodano
from .models import (AuditLog, BankTransaction, Budget, Debt, FinancialReport,
                     Invoice, MonthlyOverhead, Municipality, Overhead,
                     OverheadCategory, Salary, SalaryAddition, Tax,
                     TaxConfiguration, VariablePayRule)


class ClientSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientSupplier
        fields = "__all__"


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = "__all__"


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = "__all__"


class SalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Salary
        fields = "__all__"


class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = "__all__"


class SalaryAdditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryAddition
        fields = "__all__"


class TaxConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxConfiguration
        fields = "__all__"


class VariablePayRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariablePayRule
        fields = "__all__"


class FinancialDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialDetails
        fields = "__all__"


class OverheadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Overhead
        fields = "__all__"


class MunicipalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipality
        fields = "__all__"


class FinancialReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialReport
        fields = "__all__"


class DebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debt
        fields = "__all__"


class BankTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankTransaction
        fields = "__all__"


class OverheadCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OverheadCategory
        fields = "__all__"


class MonthlyOverheadSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonthlyOverhead
        fields = "__all__"


class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = "__all__"
