from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.db import connection, DatabaseError
from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Min, Count, Max
import logging
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.core.cache import cache

from healthharmony.models.treatment.models import Category, Illness, Certificate
from healthharmony.models.inventory.models import InventoryDetail
from healthharmony.users.models import Department, User


logger = logging.getLogger(__name__)


def getCategory(request):
    """
    Fetch all categories from the database.

    This function attempts to retrieve all Category objects from the database.
    If an exception occurs during the retrieval process, it logs the error and
    sends an error message to the user via Django's messaging framework.

    Args:
        request (HttpRequest): The HTTP request object that triggered this function.

    Returns:
        tuple: A tuple containing:
            - QuerySet: A QuerySet of all Category objects.
            - HttpRequest: The original request object, potentially modified to include error messages.
    """
    try:
        category_cache = cache.get("category_cache", {})

        categories = category_cache.get("query")

        if not categories:
            categories = Category.objects.all()
            category_cache["query"] = categories
            cache.set("category_cache", category_cache, timeout=(60 * 120))

    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        messages.error(request, "Error fetching data. Please reload.")
    return categories, request


def sort_category(categories, request):
    """
    Organize category data by filtering illnesses into yearly, monthly, and weekly ranges.

    This function iterates over a list of predefined filters ("yearly", "monthly", "weekly")
    and processes each filter by calculating date ranges. For each filter, it determines the
    start and end dates based on the current date and then invokes the `sort_category_loop`
    function to categorize and store the relevant illness data.

    Args:
        categories (QuerySet): A Django QuerySet containing Category objects to process.
        request (HttpRequest): The HTTP request object, used to send error messages if necessary.

    Returns:
        tuple: A tuple containing:
            - HttpRequest: The original request object, potentially modified to include error messages.
            - dict: A dictionary containing categorized illness data, organized by filters (yearly, monthly, weekly).

    Raises:
        None: Any exceptions encountered during processing are handled within the `sort_category_loop` function.
    """
    category_data = {}
    data_filter = ["yearly", "monthly", "weekly"]

    now = timezone.now()

    try:
        illness_cache = cache.get("illness_cache", {})

        illnesses = illness_cache.get("query")

        if not illnesses:
            illnesses = Illness.objects.all()
            illness_cache["query"] = illnesses
            cache.set("illness_cache", illness_cache, timeout=None)

    except DatabaseError as e:
        logger.info(f"{e}")
    finally:
        connection.close()

    if illness_cache.get("category_data") is not None:
        category_data = illness_cache.get("category_data")
    else:
        for filter in data_filter:
            start, max_range, date_format, date_loop = get_init_loop_params(filter, now)

            for offset in range(max_range):
                main_start, main_end = get_changing_loop_params(
                    offset, start, date_loop, filter
                )

                request, category_data = sort_category_loop(
                    categories,
                    main_start,
                    main_end,
                    category_data,
                    date_format,
                    request,
                    filter,
                    illnesses,
                )
        illness_cache["category_data"] = category_data
        cache.set("illness_cache", illness_cache, timeout=None)

    return request, category_data


def sort_category_loop(
    categories,
    main_start,
    main_end,
    category_storage,
    date_format,
    request,
    filter,
    illnesses,
):
    """
    Sort and categorize illnesses based on their update timestamps and a specified filter.

    This function iterates through a list of categories and retrieves associated illnesses
    from the database based on the category and a date range (`main_start` to `main_end`).
    The illnesses are then stored in a nested dictionary (`category_storage`) organized
    by category and date. The function handles different filtering conditions, such as
    weekly filtering, and stores the data accordingly.

    Args:
        categories (QuerySet): A Django QuerySet containing Category objects to process.
        main_start (datetime): The start date for filtering illnesses.
        main_end (datetime): The end date for filtering illnesses.
        category_storage (dict): A dictionary to store the categorized illness data.
        date_format (str): The format string used to format dates for dictionary keys.
        request (HttpRequest): The HTTP request object, used to send error messages if necessary.
        filter (str): A string that determines the filtering condition (e.g., "weekly").

    Returns:
        tuple: A tuple containing:
            - HttpRequest: The original request object, potentially modified to include error messages.
            - dict: The updated `category_storage` dictionary containing categorized illness data.

    Raises:
        None: Any exceptions encountered during processing are logged and handled
              within the function, and an error message is sent to the user.
    """

    for category in categories:
        for illness in illnesses:

            if filter not in category_storage:
                category_storage[filter] = {}
            if category.id not in category_storage[filter]:
                category_storage[filter][category.id] = {}
            if category.category not in category_storage[filter][category.id]:
                category_storage[filter][category.id][category.category] = {}
            if (
                main_start.strftime(date_format)
                not in category_storage[filter][category.id][category.category]
            ):
                category_storage[filter][category.id][category.category][
                    main_start.strftime(date_format)
                ] = []

            if illness.illness_category:

                if filter == "weekly":
                    if (
                        illness.illness_category.category == category.category
                        and illness.updated >= main_start
                        and illness.updated <= main_end
                    ):
                        category_storage[filter][category.id][category.category][
                            main_start.strftime(date_format)
                        ].append(illness_to_dict(illness))
                elif (
                    illness.illness_category.category == category.category
                    and illness.updated >= main_start
                    and illness.updated < main_end
                ):
                    category_storage[filter][category.id][category.category][
                        main_start.strftime(date_format)
                    ].append(illness_to_dict(illness))

        # try:
        #     illnesses = Illness.objects.select_related("illness_category").filter(
        #         illness_category=category, updated__gte=main_start, updated__lt=main_end
        #     )

        #     if filter == "weekly":
        #         illnesses = Illness.objects.filter(
        #             illness_category=category,
        #             updated__gte=main_start,
        #             updated__lte=main_end,
        #         )

        #     if filter not in category_storage:
        #         category_storage[filter] = {}
        #     if category.id not in category_storage[filter]:
        #         category_storage[filter][category.id] = {}
        #     if category.category not in category_storage[filter][category.id]:
        #         category_storage[filter][category.id][category.category] = {}
        #     if (
        #         main_start.strftime(date_format)
        #         not in category_storage[filter][category.id][category.category]
        #     ):
        #         category_storage[filter][category.id][category.category][
        #             main_start.strftime(date_format)
        #         ] = []

        #     if illnesses:
        #         category_storage[filter][category.id][category.category][
        #             main_start.strftime(date_format)
        #         ] = [illness_to_dict(illness) for illness in illnesses]

        # except Exception as e:
        #     logger.error(f"Failed to sort data: {str(e)}")
        #     messages.error(request, "Failed to sort data. Please try again")
        # finally:
        #     connection.close()

    return request, category_storage


def illness_to_dict(illness):
    """
    Convert an Illness object into a dictionary.

    This function takes an Illness object and converts it into a dictionary
    containing its ID, issue, category ID, and category name. This dictionary
    representation can be useful for serialization, JSON responses, or
    other operations where a structured data format is needed.

    Args:
        illness (Illness): An Illness object to be converted.

    Returns:
        dict: A dictionary containing the following keys:
            - "id" (int): The unique identifier of the illness.
            - "issue" (str): A brief description or name of the illness.
            - "category_id" (int): The unique identifier of the illness's category.
            - "category" (str): The name of the category associated with the illness.
    """
    return {
        "id": illness.id,
        "issue": illness.issue,
        "category_id": illness.illness_category.id,
        "category": illness.illness_category.category,
    }


def get_sorted_category(request):
    """
    Retrieve and sort categories along with their associated illnesses.

    This function first retrieves all categories using the `getCategory` function.
    If no categories are found or an error occurs during retrieval, it returns early.
    Otherwise, it proceeds to sort the categories and their associated illnesses by
    different time filters (yearly, monthly, weekly) using the `sort_category` function.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        tuple: A tuple containing:
            - HttpRequest: The original request object, potentially modified to include error messages.
            - dict or None: A dictionary containing the sorted category data if successful, or `None` if an error occurred during category retrieval.
    """
    categories, request = getCategory(request)

    if categories is None:
        return request, categories

    request, category_data = sort_category(categories, request)

    return request, category_data


def get_departments(request):
    """
    Fetches all Department instances from the database.

    Args:
        request: The HTTP request object. Used for logging errors and displaying messages.

    Returns:
        tuple: A tuple containing the request object and a queryset of Department instances.
    """
    try:
        # Fetch all Department instances
        department_cache = cache.get("department_cache", {})

        if not department_cache.get("query"):
            departments = Department.objects.all()
            department_cache["query"] = departments
            cache.set("department_cache", department_cache, timeout=(60 * 120))
        else:
            departments = department_cache.get("query")

    except Exception as e:
        # Log the error with a message
        logger.error(f"Failed to fetch department data: {str(e)}")
        # Add an error message to the request to inform the user
        messages.error(request, "Failed to fetch data. Please reload")
        # Return the request and an empty list of departments
        return request, []
    finally:
        connection.close()

    # Return the request and the list of departments
    return request, departments


def sort_department(
    request,
    departments,
    get_init_loop_params,
    get_changing_loop_params,
    sort_department_loop,
):
    """
    Sorts department data based on different time filters and updates the department_data dictionary.

    Args:
        request (HttpRequest): The HTTP request object, used for logging errors and messages.
        departments (QuerySet): A queryset of Department objects to be sorted.
        get_init_loop_params (function): A function to get initial loop parameters for a given filter.
        get_changing_loop_params (function): A function to get changing loop parameters for a given offset.
        sort_department_loop (function): A function to sort and process department data for each period.

    Returns:
        tuple: A tuple containing the updated request and department_data dictionary.
    """
    # Initialize the department_data dictionary with keys for each filter type
    department_data = {filter: {} for filter in ["yearly", "monthly", "weekly"]}

    # Get the current time
    now = timezone.now()

    try:
        illness_cache = cache.get("illness_cache", {})

        patients = illness_cache.get("patient_per_department")

        if not patients:
            patients = User.objects.all().annotate(
                latest_illness=Max("patient_illness__updated")
            )
            illness_cache["patient_per_department"] = patients
            cache.set("illness_cache", illness_cache, timeout=None)

    except DatabaseError as e:
        logger.warning(f"{e}")
    finally:
        connection.close()

    if illness_cache.get("department_data") is not None:
        department_data = illness_cache.get("department_data")
    else:
        # Iterate over each filter type (yearly, monthly, weekly)
        for filter in department_data:
            # Get the initial parameters for the loop based on the filter type
            start, max_range, date_format, date_loop = get_init_loop_params(filter, now)

            # Iterate through each offset value within the range for the current filter
            for offset in range(max_range):
                # Get the start and end dates for the current period
                main_start, main_end = get_changing_loop_params(
                    offset, start, date_loop, filter
                )

                # Sort and process the department data for the current period
                request, department_data = sort_department_loop(
                    departments,
                    department_data,
                    main_start,
                    main_end,
                    date_format,
                    filter,
                    request,
                    patients,
                )
        illness_cache["department_data"] = department_data
        cache.set("illness_cache", illness_cache, timeout=None)

    return request, department_data


def get_prepared_department_storage(
    department_data, department, main_start, date_format, filter
):
    """
    Prepares the department data structure for storing department information.

    Args:
        department_data (dict): The data structure to store department information.
        department (Department): The department instance to be used as a key.
        main_start (datetime): The start date for the period.
        date_format (str): The format for dates used as keys in the storage.
        filter (str): The type of filter applied, which determines the storage key.

    Returns:
        dict: The updated department_data dictionary with prepared storage for the department.
    """
    # Ensure the filter key exists in the department_data dictionary
    if filter not in department_data:
        department_data[filter] = {}

    # Ensure the department ID key exists under the filter key
    if department.id not in department_data[filter]:
        department_data[filter][department.id] = {}

    # Ensure the department name key exists under the department ID key
    if department.department not in department_data[filter][department.id]:
        department_data[filter][department.id][department.department] = {}

    # Ensure the formatted date key exists under the department name key
    if (
        main_start.strftime(date_format)
        not in department_data[filter][department.id][department.department]
    ):
        department_data[filter][department.id][department.department][
            main_start.strftime(date_format)
        ] = []

    return department_data


def get_init_loop_params(filter, now):
    """
    Initializes parameters for date looping based on the filter type.

    Args:
        filter (str): The type of filter to apply. Can be "yearly", "monthly", or "weekly".
        now (datetime): The current date and time.

    Returns:
        tuple: A tuple containing the start date, maximum range of iterations, date format, and date loop increment.
    """
    if filter == "yearly":
        # For yearly filter, set parameters to loop through months
        max_range = 12  # Number of months to loop through
        start = now - relativedelta(months=11)  # Start from 11 months ago
        date_loop = 1  # Increment by 1 month
        date_format = "%B"  # Format for month names

    if filter == "monthly":
        # For monthly filter, set parameters to loop through days
        max_range = 6  # Number of periods to loop through (e.g., 6 months)
        start = now - timedelta(days=30)  # Start from 30 days ago
        date_loop = 5  # Increment by 5 days
        date_format = "%B %d"  # Format for month and day

    if filter == "weekly":
        # For weekly filter, set parameters to loop through weeks
        start = now - timedelta(days=6)  # Start from 6 days ago
        max_range = 7  # Number of days to loop through (a week)
        date_format = "%A, %d"  # Format for day of the week and day of the month
        date_loop = 1  # Increment by 1 day

    return start, max_range, date_format, date_loop


def get_changing_loop_params(offset, start, date_loop, filter):
    """
    Calculates the start and end dates for each period based on the filter type.

    Args:
        offset (int): The offset value to calculate the period start.
        start (datetime): The base start date for calculations.
        date_loop (int): The loop increment for the filter type (e.g., number of months, days).
        filter (str): The type of filter to apply. Can be "yearly", "monthly", or "weekly".

    Returns:
        tuple: A tuple containing the calculated start date and end date for the period.
    """
    if filter == "yearly":
        # For yearly filter, calculate the start and end of the month
        main_start = start + relativedelta(months=offset, day=1)
        main_end = main_start + relativedelta(months=date_loop)

    if filter == "monthly":
        # For monthly filter, calculate the start and end of the period
        main_start = start + timedelta(days=offset * date_loop)
        main_end = main_start + timedelta(days=date_loop)

    if filter == "weekly":
        # For weekly filter, calculate the start and end of the week
        new_start = start + timedelta(days=offset * date_loop)
        main_start = new_start.replace(hour=0, minute=0, second=0, microsecond=0)
        main_end = new_start.replace(hour=23, minute=59, second=59, microsecond=999999)

    return main_start, main_end


def sort_department_loop(
    departments,
    department_data,
    main_start,
    main_end,
    date_format,
    filter,
    request,
    patients,
):
    """
    Processes and sorts department data for a given time period and updates the department_data dictionary.

    Args:
        departments (QuerySet): A queryset of Department objects to process.
        department_data (dict): The dictionary to store sorted department data.
        main_start (datetime): The start date for the current period.
        main_end (datetime): The end date for the current period.
        date_format (str): The date format used as the key in department_data.
        filter (str): The type of filter applied (e.g., "yearly", "monthly", "weekly").
        request (HttpRequest): The HTTP request object, used for logging errors and messages.

    Returns:
        tuple: A tuple containing the updated request and department_data dictionary.
    """

    for department in departments:
        # Prepare the department data storage structure for the current department
        department_data = get_prepared_department_storage(
            department_data, department, main_start, date_format, filter
        )

        if patients:
            for patient in patients:
                if patient.department and patient.latest_illness:
                    if (
                        patient.department.id == department.id
                        and patient.latest_illness >= main_start
                        and patient.latest_illness <= main_end
                    ):
                        department_data[filter][department.id][department.department][
                            main_start.strftime(date_format)
                        ].append(
                            {
                                "patientId": patient.id,
                                "department": patient.department.department,
                            }
                        )

        # try:
        #     # Query for patients associated with the current department and within the specified date range
        #     patients = (
        #         User.objects.select_related("department")
        #         .filter(
        #             department=department,
        #             patient_illness__updated__gte=main_start,
        #             patient_illness__updated__lte=main_end,
        #         )
        #         .distinct()
        #     )

        #     # If there are patients, add their information to the department_data dictionary
        #     if patients:
        #         department_data[filter][department.id][department.department][
        #             main_start.strftime(date_format)
        #         ] = [
        #             {
        #                 "patientId": patient.id,
        #                 "department": patient.department.department,
        #             }
        #             for patient in patients
        #         ]

        # except Exception as e:
        #     # Log the error and add an error message to the request if sorting fails
        #     logger.error(f"Failed to sort department data: {str(e)}")
        #     messages.error(request, "Failed to sort data. Please try again")
        # finally:
        #     connection.close()

    return request, department_data


def get_sorted_department(request):
    """
    Retrieves and sorts department data based on various time filters.

    Args:
        request (HttpRequest): The HTTP request object used for logging errors and messages.

    Returns:
        tuple: A tuple containing the updated request and the department_data dictionary, or None if there are no departments.
    """
    # Fetch all departments and update the request with any potential errors
    request, departments = get_departments(request)

    # If no departments are found, return the updated request and None for departments
    if departments is None:
        return request, departments

    # Sort department data based on various filters and update the request with any potential errors
    request, department_data = sort_department(
        request,
        departments,
        get_init_loop_params,
        get_changing_loop_params,
        sort_department_loop,
    )

    return request, department_data


def get_inventory(request):
    inventory = None
    try:
        inventory = (
            InventoryDetail.objects.all()
            .annotate(total_quantity=Sum("quantities__updated_quantity"))
            .values("id", "item_name", "category", "expiration_date", "total_quantity")
        )

    except Exception as e:
        messages.error(
            request, "Failure to connect to the server. Please reload the page"
        )
        logger.error(f"Faild to fetch the inventory data: {str(e)}")

    return request, inventory


def get_sorted_inventory_list(request):
    inventory = None
    try:
        inventory_cache = cache.get("inventory_cache", {})

        inventory = inventory_cache.get("inventory_detailed")

        if not inventory:
            inventory = (
                InventoryDetail.objects.all()
                .annotate(total_quantity=Sum("quantities__updated_quantity"))
                .values(
                    "id",
                    "total_quantity",
                    "item_name",
                    "category",
                    "expiration_date",
                    "item_no",
                    "description",
                    "unit",
                )
            )

            if inventory:
                for data in inventory:
                    if data["total_quantity"] is None:
                        data["total_quantity"] = 0
                    if data["expiration_date"] is not None:
                        data["expiration_date"] = data["expiration_date"].isoformat()
                    else:
                        data["expiration_date"] = ""
                    if data["category"] == "Medicine":
                        data["sorter"] = 1
                    if data["category"] == "Supply":
                        data["sorter"] = 2
            inventory_cache["inventory_detailed"] = inventory
            cache.set("inventory_detailed", inventory, timeout=(60 * 120))

    except Exception as e:
        logger.error(f"Failed to fetch sorted inventory list: {str(e)}")
        messages.error(request, "Requested data not fetched. Please reload page")
    finally:
        connection.close()

    return request, list(inventory)


def get_counted_inventory(request):
    try:
        categories = ["Medicine", "Supply"]
        filters = ["yearly", "monthly", "weekly"]
        inventory_data = {
            category: {filter: {} for filter in filters} for category in categories
        }

        now = timezone.now()
        inventory_cache = cache.get("inventory_cache", {})

        if inventory_cache.get("inventory_data"):
            inventory_data = inventory_cache.get("inventory_data")
        else:

            for category in inventory_data:

                for filter in inventory_data[category]:
                    start, max_range, date_format, date_loop = get_init_loop_params(
                        filter, now
                    )

                    for offset in range(max_range):
                        main_start, main_end = get_changing_loop_params(
                            offset, start, date_loop, filter
                        )
                        inventory = InventoryDetail.objects.filter(
                            category=category,
                            quantities__timestamp__gte=main_start,
                            quantities__timestamp__lte=main_end,
                        ).annotate(
                            total_quantity=Sum("quantities__updated_quantity"),
                            date_updated=Min("quantities__timestamp"),
                        )
                        inventory_data[category][filter][
                            main_start.strftime(date_format)
                        ] = []
                        if inventory:
                            for data in inventory:
                                data.total_quantity = data.total_quantity or 0
                                inventory_data[category][filter][
                                    main_start.strftime(date_format)
                                ].append(
                                    {
                                        "id": data.id,
                                        "total_quantity": data.total_quantity,
                                        "expiration_date": data.expiration_date.isoformat()
                                        if data.expiration_date
                                        else "",
                                        "date_updated": data.date_updated.isoformat(),
                                    }
                                )
            inventory_cache["inventory_data"] = inventory_data
            cache.set("inventory_cache", inventory_cache, timeout=(60 * 120))

    except Exception as e:
        logger.error(str(e))
        messages.error(request, "Failed to fetch inventory data.")
        inventory_data = None
    finally:
        connection.close()

    return request, inventory_data


def fetch_today_patient(now):
    try:
        count = cache.get("today_patient")
        if not count:
            count = (
                User.objects.filter(patient_illness__updated__date=now.date())
                .distinct()
                .count()
                or 0
            )
            cache.set("today_patient", count, timeout=(60 * 30))
    except DatabaseError as e:
        logger.info(f"{e}")
        count = 0
    finally:
        connection.close()
    return count


def fetch_total_patient():
    try:
        count = cache.get("total_patient")

        if not count:

            count = (
                User.objects.annotate(illness_count=Count("patient_illness"))
                .filter(illness_count__gt=0)
                .count()
                or 0
            )
            cache.set("total_patient", count, timeout=(60 * 30))

    except DatabaseError as e:
        logger.info(f"{e}")
        count = 0
    finally:
        connection.close()
    return count


def fetch_previous_patients(previous_day):
    try:
        count = cache.get("previous_patients")

        if not count:
            count = (
                User.objects.filter(patient_illness__updated__date=previous_day.date())
                .distinct()
                .count()
                or 0
            )

            cache.set("previous_patients", count, timeout=(60 * 30))

    except DatabaseError as e:
        logger.info(f"{e}")
        count = 0
    finally:
        connection.close()
    return count


def fetch_monthly_medcert(now, previous_month):
    monthly_medcert = 0
    previous_medcert = 0
    try:
        certificate_cache = cache.get("certificate_cache", {})

        medcerts = certificate_cache.get("query")

        if not medcerts:
            medcerts = Certificate.objects.filter(released=True)

            if medcerts:
                certificate_cache["query"] = medcerts

                for cert in medcerts:
                    if (
                        cert.requested.month == now.month
                        and cert.requested.year == now.year
                    ):
                        monthly_medcert += 1
                    if (
                        cert.requested.month == previous_month.month
                        and cert.requested.year == previous_month.year
                    ):
                        previous_medcert += 1
                certificate_cache["monthly_medcert"] = monthly_medcert
                certificate_cache["previous_medcert"] = previous_medcert

            cache.set("certificate_cache", certificate_cache, timeout=(60 * 120))
        else:
            monthly_medcert = certificate_cache.get("monthly_medcert", 0)
            previous_medcert = certificate_cache.get("previous_medcert", 0)

    except DatabaseError as e:
        logger.info(f"{e}")

    return monthly_medcert, previous_medcert


def fetch_previous_medcert(previous_month):
    try:
        count = (
            Certificate.objects.filter(
                requested__month=previous_month.month,
                requested__year=previous_month.year,
                released=True,
            ).count()
            or 0
        )
    except DatabaseError as e:
        logger.info(f"{e}")
        count = 0
    finally:
        connection.close()
    return count


def fetch_patients():
    try:
        user_cache = cache.get("user_cache", {})

        if not user_cache.get("patients"):
            patients = User.objects.filter(access=1)
            user_cache["patients"] = patients
            cache.set("user_cache", user_cache, timeout=(60 * 120))
        else:
            patients = user_cache.get("patients")
    except DatabaseError as e:
        logger.info(f"{e}")
        patients = None
    finally:
        connection.close()
    return patients


def fetch_categories():
    try:
        category_cache = cache.get("category_cache", {})

        if not category_cache.get("query"):
            category = Category.objects.all()
            category_cache["query"] = category
            cache.set("category_cache", category_cache, timeout=None)
        else:
            category = category_cache.get("query")
    except DatabaseError as e:
        logger.info(f"{e}")
        category = None
    finally:
        connection.close()
    return category


def fetch_inventory(InventoryDetail, Sum, request):
    inventory = None
    try:
        inventory_cache = cache.get("inventory_cache", {})

        inventory = inventory_cache.get("inventory_table")

        if not inventory:
            inventory = (
                InventoryDetail.objects.all()
                .annotate(
                    quantity=Sum("quantities__updated_quantity"),
                )
                .values("id", "item_name", "category", "quantity", "expiration_date")
            )

            if inventory:
                for data in inventory:
                    if data["expiration_date"]:
                        data["expiration_date"] = data["expiration_date"].isoformat()
                    data["quantity"] = data["quantity"] or 0

            inventory_cache["inventory_table"] = inventory

            cache.set("inventory_cache", inventory_cache, timeout=(60 * 120))

    except Exception as e:
        logger.error(f"Failed to fetch inventory data: {str(e)}")
        messages.error(request, "Failed to fetched inventory data. Please reload page.")
    finally:
        connection.close()
    return request, inventory


def fetch_history(Illness, IllnessSerializer):
    history = None
    history_data = None
    try:
        illness_cache = cache.get("illness_cache", {})
        history = illness_cache.get("query")
        history_data = illness_cache.get("illness_data")

        if not history:
            history = Illness.objects.all()
            illness_cache["query"] = history
            cache.set("illness_cache", illness_cache, timeout=(60 * 120))

        if not history_data:
            history_data = []

            for hist in history:
                data = IllnessSerializer(hist)
                history_data.append(data.data)

            illness_cache["illness_data"] = history_data
            cache.set("illness_cache", illness_cache, timeout=(60 * 120))

    except Exception as e:
        logger.info(f"{e}")
    finally:
        connection.close()
    return history, history_data


def fetch_certificate_chart(timezone, Certificate, relativedelta):
    certificate_chart = {}

    cert_dates = ["yearly", "monthly", "weekly"]

    now = timezone.now()

    start = now - relativedelta(months=11)

    certificate_cache = cache.get("certificate_cache", {})
    certificates = certificate_cache.get("query")
    certificate_chart = certificate_cache.get("certificate_chart")

    if not certificates:
        certificates = Certificate.objects.all()
        connection.close()
        certificate_cache["query"] = certificates
        cache.set("certificate_cache", certificate_cache, timeout=(60 * 120))

    if not certificate_chart:
        certificate_chart = {}
        for cert_date in cert_dates:
            start, max_range, date_format, date_loop = get_init_loop_params(
                cert_date, now
            )
            certificate_chart[cert_date] = []
            for offset in range(max_range):
                main_start, main_end = get_changing_loop_params(
                    offset, start, date_loop, cert_date
                )
                count = 0
                if certificates:
                    for cert in certificates:
                        if cert.requested >= main_start and cert.requested < main_end:
                            count = count + 1
                certificate_chart[cert_date].append(
                    {f"{main_start.strftime(date_format)}": count}
                )
        certificate_cache["certificate_chart"] = certificate_chart
        cache.set("certificate_cache", certificate_cache, timeout=(60 * 120))

    return certificate_chart


def fetch_certificates(Certificate, F):
    certificate_cache = cache.get("certificate_cache", {})
    certificates = certificate_cache.get("certificates_detailed")
    if not certificates:
        certificates = (
            Certificate.objects.all()
            .annotate(
                email=F("patient__email"),
                first_name=F("patient__first_name"),
                last_name=F("patient__last_name"),
            )
            .values(
                "id",
                "patient",
                "purpose",
                "requested",
                "is_ready",
                "released",
                "email",
                "first_name",
                "last_name",
            )
        )

        if certificates:
            for cert in certificates:
                cert["requested"] = cert["requested"].isoformat()
        certificate_cache["certificates_detailed"] = certificates
        cache.set("certificate_cache", certificate_cache, timeout=(60 * 120))

    connection.close()

    return certificates


def fetch_employees(
    OuterRef, Coalesce, Subquery, Value, DateTimeField, messages, request
):
    try:
        cases = (
            Illness.objects.filter(staff=OuterRef("pk"))
            .order_by("-updated")
            .values("updated")[:1]
        )
        users = (
            User.objects.filter(access__gte=2, access__lte=3)
            .annotate(
                last_case=Coalesce(
                    Subquery(cases), Value(None), output_field=DateTimeField()
                ),
                staff_count=Count("staff_illness"),
                doctor_count=Count("doctor_illness"),
            )
            .values()
        )
        for user in users:
            if user["DOB"]:
                user["DOB"] = user["DOB"].isoformat()
            if user["last_case"]:
                user["last_case"] = user["last_case"].isoformat()
            if user["date_joined"]:
                user["date_joined"] = user["date_joined"].isoformat()
        logger.info(
            f"{request.user.email} successfully fetched employee instances in staff/accounts"
        )
    except Exception as e:
        messages.error(request, "Failed to fetch necessary data. Please reload page")
        logger.error(
            f"{request.user.email} failed to fetched employee instances in staff/accounts: {str(e)}"
        )
    return users


def send_welcome_email(patient, password):
    subject = "Welcome to HealthHarmony!"
    from_email = settings.EMAIL_HOST_USER

    body = render_to_string(
        "email/welcome_email.html", {"patient": patient, "password": password}
    )

    recipient_list = [patient.email]
    email = EmailMessage(subject, body, from_email, recipient_list)
    email.content_subtype = "html"
    email.send()
