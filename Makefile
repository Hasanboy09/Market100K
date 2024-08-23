app:
	python manage.py startapp apps
mig:
	python manage.py makemigrations
	python manage.py migrate

user:
	python manage.py createsuperuser
fixture-product:
	python manage.py dumpdata apps.Product --output=apps/fixtures/Product.json


fixture-category:
	python manage.py dumpdata apps.Product --output=apps/fixtures/Category.json




