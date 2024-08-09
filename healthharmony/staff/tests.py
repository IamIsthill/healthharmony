import os
import django
from django.test import RequestFactory
import json


def main():
    # Set the Django settings module environment variable
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "healthharmony.app.settings")

    # Setup Django
    django.setup()

    # Import the function after setting up Django
    from healthharmony.staff.functions import get_departments, sort_department

    # Initialize RequestFactory and create a dummy GET request
    factory = RequestFactory()
    request = factory.get(
        "/dummy-url/"
    )  # The URL here doesn't matter; it's just a placeholder

    # Call the function with the dummy request
    request, departments = get_departments(request)

    # Print the retrieved department data
    request, department_data = sort_department(request, departments)
    print(json.dumps(department_data, indent=4, sort_keys=True))


if __name__ == "__main__":
    main()
