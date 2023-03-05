from django.urls import path

from app.views import ImportPlansAPIView, UserCreditsView, PlansPerformanceView

urlpatterns = [
    path("user_credits/<int:user_id>/", UserCreditsView.as_view(), name="user_credits"),
    path("plans_insert/", ImportPlansAPIView.as_view(), name="import_plans"),
    path("plans_performance/", PlansPerformanceView.as_view(), name="plans_performance"),
]
app_name = "app"
