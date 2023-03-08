from django.db.models import Sum
from django.shortcuts import render
import datetime

from rest_framework import generics, status
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView


from .models import Credits, Plans, Payments
from .serializers import (
    OpenCreditSerializer,
    ImportPlansSerializer,
)
from .service import import_plans_from_excel


class UserCreditsView(generics.ListAPIView):
    serializer_class = OpenCreditSerializer

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        credits = Credits.objects.filter(user_id=user_id).prefetch_related("payments")
        return credits

    def list(self, request, *args, **kwargs):
        user_id = self.kwargs["user_id"]
        if not Credits.objects.filter(user_id=user_id).exists():
            return Response(
                {"error": f"No credits found for user with id={user_id}"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return super().list(request, *args, **kwargs)


class ImportPlansAPIView(APIView):
    parser_classes = [FileUploadParser]

    def get(self, request):
        return render(request, "import_plans.html")

    def post(self, request, *args, **kwargs):
        serializer = ImportPlansSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data["file"]
        if not file:
            return Response({"error": "No file uploaded."}, status=400)

        try:
            import_plans_from_excel(file)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

        return Response({"success": "Plans imported successfully."}, status=200)


class PlansPerformanceView(APIView):
    def get(self, request, *args, **kwargs):
        date = request.GET.get("date")

        if not date:
            return Response({"error": 'Missing required parameter "date"'})

        try:
            date = datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return Response(
                {"error": 'Invalid date format. Date should be in format "YYYY-MM-DD"'}
            )

        month = date.month
        year = date.year
        plans = Plans.objects.filter(period__year=year, period__month=month)

        results = []

        for plan in plans:
            plan_category = plan.category_id.name
            plan_sum = plan.sum
            period_start = datetime.datetime(year=year, month=month, day=1)
            period_end = date

            result = {}
            if plan_category == "видача":
                credits_sum = (
                    Credits.objects.filter(
                        issuance_date__range=(period_start, period_end)
                    ).aggregate(Sum("body"))["body__sum"]
                    or 0
                )
                result = {
                    "month": month,
                    "category": plan_category,
                    "plan_sum": plan_sum,
                    "actual_sum": credits_sum,
                    "percent": round(credits_sum / plan_sum * 100, 2)
                    if plan_sum
                    else 0,
                }

            elif plan_category == "збір":
                payments_sum = (
                    Payments.objects.filter(
                        payment_date__range=(period_start, period_end),
                    ).aggregate(Sum("sum"))["sum__sum"]
                    or 0
                )
                result = {
                    "month": month,
                    "category": plan_category,
                    "plan_sum": plan_sum,
                    "actual_sum": payments_sum,
                    "percent": round(payments_sum / plan_sum * 100, 2)
                    if plan_sum
                    else 0,
                }

            results.append(result)

        return Response(results)
