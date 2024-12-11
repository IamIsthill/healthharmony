HealthHarmony: An Information Management System for DHVSU Medical and Dental Services with Data Analytics
=======================================================================================================

Installation
-------------
1. **Install Poetry**

    Follow the [Poetry installation guide](https://python-poetry.org/docs/#installation) if you don't have Poetry installed.

2. **Install NPM (Node Package Manager)**

    Follow the [NPM installation guide](https://nodejs.org/en/download/package-manager) if you don't have NPM installed..
3. **Install the Dependencies**

    .. code-block:: bash

        poetry install
        npm install

4. **Create a `.env` File**

    Create a `.env` file in the `healthharmony` directory and add the required environment variables. Example:

    .. code-block:: .env

        DEBUG=True
        PROD=False
        IN_DOCKER=False

        INCLUDE_ADMIN=True
        WEATHER=your-weather-api-key

        EMAIL_ADD=your-email-address
        EMAIL_PASS=your-email-pass

5. **Run Database Migrations**

    .. code-block:: bash

        poetry run python -m healthharmony.manage migrate

6. **Create a Superuser for the Admin Interface**

    .. code-block:: bash

        poetry run python -m healthharmony.manage createsuperuser

7. **Run the Development Server**

    .. code-block:: bash

        poetry run python -m healthharmony.manage runserver


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


Troubleshooting
----------------
- Ensure your `.env` file contains all the required variables.
- Verify that you have applied all migrations.
- Check the logs for any errors and consult Django documentation or community forums for solutions.

License
--------
This project is licensed under the MIT License.

Contact
--------
For questions or feedback, please contact `bercasiocharles14@gmail.com`_.

Acknowledgements
----------------
- Django
- Django Rest Framework
- Contributors and maintainers

.. _bercasiocharles14@gmail.com: mailto:bercasiocharles14@gmail.com
