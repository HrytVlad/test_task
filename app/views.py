import os
import tempfile

from django.http import HttpResponse, FileResponse
from django.shortcuts import render
from django.utils.encoding import smart_str
from rest_framework import generics
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView


from .models import Credits
from .serializers import (
    OpenCreditSerializer,
    ClosedCreditSerializer,
    ImportPlansSerializer,
)
from .service import import_plans_from_excel


class UserCreditsView(generics.ListAPIView):
    serializer_class = OpenCreditSerializer

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        return Credits.objects.filter(user_id=user_id)

    def get_serializer_class(self):
        queryset = self.get_queryset()
        if (
            queryset.exists()
            and queryset.filter(actual_return_date__isnull=False).exists()
        ):
            return ClosedCreditSerializer
        return self.serializer_class


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

        # Return the file as a response
        response = FileResponse(file, as_attachment=True, filename=file.name)
        return response
