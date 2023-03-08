from _decimal import Decimal
from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers
from .models import Credits, Payments


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payments
        fields = ("sum", "payment_date", "type_id")


class ClosedCreditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credits
        fields = [
            "issuance_date",
            "is_closed",
            "actual_return_date",
            "body",
            "percent",
            "total_payments",
        ]

    total_payments = serializers.SerializerMethodField()

    def get_total_payments(self, obj):
        payments = obj.payments.all()
        total_payments = Decimal(0)
        for payment in payments:
            total_payments += payment.sum
        return total_payments


class OpenCreditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credits
        fields = [
            "issuance_date",
            "is_closed",
            "return_date",
            "is_overdue",
            "body",
            "percent",
            "body_payments_sum",
            "interest_payments_sum",
        ]

    is_overdue = serializers.SerializerMethodField()
    body_payments_sum = serializers.SerializerMethodField()
    interest_payments_sum = serializers.SerializerMethodField()

    def get_is_overdue(self, obj):
        if obj.actual_return_date is None and obj.return_date < timezone.now():
            overdue_days = (timezone.now() - obj.return_date).days
            return overdue_days
        return 0

    def get_body_payments_sum(self, obj):
        return Payments.objects.filter(
            credit_id=obj.id, type_id__name="тіло"
        ).aggregate(Sum("sum"))["sum__sum"] or Decimal(0)

    def get_interest_payments_sum(self, obj):
        return Payments.objects.filter(
            credit_id=obj.id, type_id__name="відсотки"
        ).aggregate(Sum("sum"))["sum__sum"] or Decimal(0)

    def to_representation(self, instance):
        if instance.actual_return_date:
            return ClosedCreditSerializer(instance).data
        else:
            return super().to_representation(instance)


class ImportPlansSerializer(serializers.Serializer):
    file = serializers.FileField()

    class Meta:
        fields = ["file"]
