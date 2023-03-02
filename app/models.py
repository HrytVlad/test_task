from django.db import models
from django.utils import timezone


class User(models.Model):
    login = models.CharField(max_length=255)
    registration_date = models.DateTimeField(default=timezone.now())

    class Meta:
        ordering = ["registration_date"]

    def __str__(self):
        return self.login


class Credits(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, primary_key=True)
    issuance_date = models.DateTimeField(default=timezone.now)
    return_date = models.DateTimeField()
    actual_return_date = models.DateTimeField(blank=True, null=True)
    body = models.IntegerField()
    percent = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        ordering = ["issuance_date"]

    def __str__(self):
        return f"{self.user_id.login} {self.issuance_date}"


class Dictionary(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Plans(models.Model):
    period = models.DateTimeField()
    sum = models.IntegerField()
    category_id = models.ForeignKey(Dictionary, on_delete=models.CASCADE)

    class Meta:
        ordering = ["period"]

    def __str__(self):
        return f"{self.id} {self.sum}"


class Payments(models.Model):
    sum = models.DecimalField(max_digits=5, decimal_places=2)
    payment_date = models.DateTimeField()
    credit_id = models.ForeignKey(Credits, on_delete=models.CASCADE)
    type_id = models.ForeignKey(Dictionary, on_delete=models.CASCADE)

    class Meta:
        ordering = ["payment_date"]

    def __str__(self):
        return f"{self.payment_date} {self.sum}"
