# test_task

### Requirements:
1. /user_credits/{user_id}/ Метод має повертати список з інформацією про всі кредити клієнта з id = **user_id** та містити наступну інформацію:
2. /plans_insert/ Метод для завантаження планів на новий місяць
3. /plans_performance/ Метод для отримання інформації про виконання планів на певну дату

### Technologies to use:
1. Python 3.7+
2. Framework DRF/Django
3. СКБД MySQL

### How to run:
1. pip install django
2. pip install django-rest-framework
3. python manage.py makemigrations
4. python manage.py migrate
5. in python console `from app.service import save_data_from_cvs_file`
6. in python console `save_data_from_cvs_file()` for save data from cvs file in db