from django.contrib import admin
from .models import Credits, User, Plans, Payments, Dictionary


admin.site.register(User)
admin.site.register(Payments)
admin.site.register(Credits)
admin.site.register(Dictionary)
admin.site.register(Plans)
