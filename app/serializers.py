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
    total_payments = serializers.SerializerMethodField()

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

    def get_total_payments(self, obj):
        payments = obj.payments_set.all()
        return payments.aggregate(Sum("sum"))["sum__sum"]


class OpenCreditSerializer(serializers.ModelSerializer):
    overdue_days = serializers.SerializerMethodField()
    body_payments_sum = serializers.SerializerMethodField()
    interest_payments_sum = serializers.SerializerMethodField()

    class Meta:
        model = Credits
        fields = (
            "return_date",
            "overdue_days",
            "body",
            "percent",
            "body_payments_sum",
            "interest_payments_sum",
        )

    def get_overdue_days(self, obj):
        if obj.actual_return_date is None and obj.return_date < timezone.now():
            return (timezone.now() - obj.return_date).days
        else:
            return None

    def get_body_payments_sum(self, obj):
        body_payments_sum = Payments.objects.filter(
            credit_id=obj.id, type_id__name="тіло"
        ).aggregate(Sum("sum"))["sum__sum"]
        return body_payments_sum or Decimal(0)

    def get_interest_payments_sum(self, obj):
        interest_payments_sum = Payments.objects.filter(
            credit_id=obj.id, type_id__name="відсотки"
        ).aggregate(Sum("sum"))["sum__sum"]
        return interest_payments_sum


class ImportPlansSerializer(serializers.Serializer):
    file = serializers.FileField()

    class Meta:
        fields = ["file"]
