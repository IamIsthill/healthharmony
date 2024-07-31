HealthHarmony: An Information Management System for DHVSU Medical and Dental Services with Data Analytics
=====================

A Django-based application for managing health records and certificates.

Features
---------
- User management
- Health record tracking
- Certificate management
- Dashboard visualization

Requirements
-------------
- Python 3.12
- Django 4.x
- Django Rest Framework
- PostgreSQL (or another supported database)
- `django-environ` for environment variable management

Installation
-------------
1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/your-repository.git
    cd your-repository
    ```

2. Create and activate a virtual environment:

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

3. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the `healthharmony` directory and add the required environment variables. Example:

    ```env
    DEBUG=True
    SECRET_KEY=your-secret-key
    DATABASE_URL=postgres://user:password@localhost:5432/yourdatabase
    CLIENT_ID=your-client-id
    ALLOWED_HOSTS=localhost,127.0.0.1
    ```

5. Run database migrations:

    ```bash
    python manage.py migrate
    ```

6. Create a superuser for the admin interface:

    ```bash
    python manage.py createsuperuser
    ```

7. Run the development server:

    ```bash
    python manage.py runserver
    ```

Usage
------
- Access the application at `http://127.0.0.1:8000/`.
- Admin interface is available at `http://127.0.0.1:8000/admin/`.

Contributing
-------------
1. Fork the repository and create a new branch for your feature or bug fix.
2. Install dependencies in your local environment.
3. Make your changes and test thoroughly.
4. Submit a pull request with a clear description of your changes.

Testing
--------
- To run tests, use:

    ```bash
    python manage.py test
    ```

- For coverage reports, you may use:

    ```bash
    coverage run manage.py test
    coverage report
    ```

Troubleshooting
----------------
- Ensure your `.env` file contains all the required variables.
- Verify that you have applied all migrations.
- Check the logs for any errors and consult Django documentation or community forums for solutions.

License
--------
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

Contact
--------
For questions or feedback, please contact [bercasiocharles14.com](mailto:bercasiocharles14.com).

Acknowledgements
----------------
- Django
- Django Rest Framework
- `django-environ`
- Contributors and maintainers
