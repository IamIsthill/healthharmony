HealthHarmony: An Information Management System for DHVSU Medical and Dental Services with Data Analytics
=======================================================================================================

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
- Poetry for dependency management

Installation
-------------
1. **Clone the Repository**

    .. code-block:: bash

        git clone https://github.com/yourusername/your-repository.git
        cd your-repository

2. **Install Poetry**

    Follow the [Poetry installation guide](https://python-poetry.org/docs/#installation) if you don't have Poetry installed.

3. **Install the Dependencies**

    .. code-block:: bash

        poetry install

4. **Create a `.env` File**

    Create a `.env` file in the `healthharmony` directory and add the required environment variables. Example:

    .. code-block:: env

        DEBUG=True
        SECRET_KEY=your-secret-key
        DATABASE_URL=postgres://user:password@localhost:5432/yourdatabase
        CLIENT_ID=your-client-id
        ALLOWED_HOSTS=localhost,127.0.0.1

5. **Run Database Migrations**

    .. code-block:: bash

        poetry run python manage.py migrate

6. **Create a Superuser for the Admin Interface**

    .. code-block:: bash

        poetry run python manage.py createsuperuser

7. **Run the Development Server**

    .. code-block:: bash

        poetry run python manage.py runserver

8. **Run Makefile Commands**

    To ensure all configurations and additional steps are applied, run:

    .. code-block:: bash

        make update

Usage
------
- Access the application at `http://127.0.0.1:8000/`.
- Admin interface is available at `http://127.0.0.1:8000/admin/`.

Contributing
-------------
1. Fork the repository and create a new branch for your feature or bug fix.
2. Install dependencies in your local environment using Poetry.
3. Make your changes and test thoroughly.
4. Submit a pull request with a clear description of your changes.

Testing
--------
- To run tests, use:

    .. code-block:: bash

        poetry run python manage.py test

- For coverage reports, you may use:

    .. code-block:: bash

        poetry run coverage run manage.py test
        poetry run coverage report

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
For questions or feedback, please contact `bercasiocharles14@gmail.com`_.

Acknowledgements
----------------
- Django
- Django Rest Framework
- `django-environ`
- Contributors and maintainers

.. _bercasiocharles14@gmail.com: mailto:bercasiocharles14@gmail.com
