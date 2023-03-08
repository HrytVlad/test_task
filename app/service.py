import csv
import os
from datetime import datetime
import pandas as pd

from app.models import User, Credits, Dictionary, Plans, Payments


dir_path = os.path.dirname(os.path.realpath(__file__))


def process_csv_user():
    file_path = os.path.join(dir_path, "users.csv")
    with open(file_path, "r") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            user = User(
                id=row["id"],
                login=row["login"],
                registration_date=datetime.strptime(
                    row["registration_date"], "%d.%m.%Y"
                ).date(),
            )
            user.save()


def process_csv_credits():
    file_path = os.path.join(dir_path, "credits.csv")
    with open(file_path, "r") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            if row["actual_return_date"]:
                actual_return_date = datetime.strptime(
                    row["actual_return_date"], "%d.%m.%Y"
                ).date()
            else:
                actual_return_date = None
            credit = Credits(
                id=row["id"],
                user_id=User.objects.get(id=row["user_id"]),
                issuance_date=datetime.strptime(
                    row["issuance_date"], "%d.%m.%Y"
                ).date(),
                return_date=datetime.strptime(row["return_date"], "%d.%m.%Y").date(),
                actual_return_date=actual_return_date,
                body=row["body"],
                percent=row["percent"],
            )
            credit.save()


def process_csv_dictionary():
    file_path = os.path.join(dir_path, "dictionary.csv")
    with open(file_path, "r", encoding="UTF-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            dictionary = Dictionary(
                id=row["id"],
                name=row["name"],
            )
            dictionary.save()


def process_csv_plans():
    file_path = os.path.join(dir_path, "plans.csv")
    with open(file_path, "r") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            plans = Plans(
                id=row["id"],
                period=datetime.strptime(row["period"], "%d.%m.%Y").date(),
                sum=row["sum"],
                category_id=Dictionary.objects.get(id=row["category_id"]),
            )
            plans.save()


def process_csv_payments():
    file_path = os.path.join(dir_path, "payments.csv")
    with open(file_path, "r") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            payments = Payments(
                id=row["id"],
                sum=row["sum"],
                payment_date=datetime.strptime(row["payment_date"], "%d.%m.%Y").date(),
                credit_id=Credits.objects.get(id=row["credit_id"]),
                type_id=Dictionary.objects.get(id=row["type_id"]),
            )
            payments.save()


def save_data_from_cvs_file():
    process_csv_user()
    process_csv_credits()
    process_csv_dictionary()
    process_csv_plans()
    process_csv_payments()


def import_plans_from_excel(file):
    df = pd.read_excel(file)

    for index, row in df.iterrows():
        period = row["місяць плану"]
        category_name = row["назва категорії плану"]
        amount = row["сума"]

        if Plans.objects.filter(
            period=period, category_id__name=category_name
        ).exists():
            raise ValueError(
                f"Plan for period {period} and category {category_name} already exists."
            )

        if period.day != 1:
            raise ValueError("Period should be the first day of the month.")

        if pd.isna(amount):
            raise ValueError("Sum column must not contain empty values.")

        category = Dictionary.objects.get(name=category_name)

        plan = Plans(period=period, sum=amount, category_id=category)
        plan.save()
