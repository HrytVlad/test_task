from rest_framework import generics
from .models import Credits
from .serializers import OpenCreditSerializer, ClosedCreditSerializer


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
