from healthharmony.models.treatment.models import Illness, Certificate

import logging
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from collections import defaultdict
from django.db.models import F


logger = logging.getLogger(__name__)


"""GET VISIT DATA"""


def get_actual_visit_data(user, main_start, main_end, date_string, visit_data, date):
    """Get the actual count of visit data"""
    try:
        count = Illness.objects.filter(
            patient=user, added__gte=main_start, added__lt=main_end
        ).count()
        visit_data[date][main_start.strftime(date_string)] = count or 0

        return visit_data

    except Exception as e:
        logger.error(f"Error getting visit data for user {user.id}: {e}")
        return None


def init_params(date):
    """
    Initialize visit parameters based on the date filter.

    Args:
        date (str): The date filter, can be "week", "month", or "year".

    Returns:
        tuple: start (datetime), max_range (int), date_string (str), date_loop (int)
    """
    now = timezone.now()

    if date == "week":
        start = now - timedelta(days=6)
        max_range = 7
        date_string = "%A, %d"
        date_loop = 1
    if date == "month":
        start = now - timedelta(days=30)
        max_range = 6
        date_string = "%B, %d"
        date_loop = 5
    if date == "year":
        start = now - timedelta(days=365)
        max_range = 13
        date_string = "%B"
        date_loop = 1

    return start, max_range, date_string, date_loop


def update_context_visit_data(user, context):
    """
    Update the context with visit data for the user.

    Args:
        user (User): The user for whom to update the visit data.
        context (dict): The context to update with visit data.

    Returns:
        dict: The updated context.
    """
    visit_data = defaultdict(lambda: defaultdict(int))
    date_filter = ["week", "month", "year"]

    # loop over the date filter
    for date in date_filter:
        # initialize the needed parameters based on the current value of date filter
        start, max_range, date_string, date_loop = init_params(date)
        for offset in range(max_range):
            # Further initilize the value of the main_start and main_end
            if date == "month":
                main_start = start + timedelta(days=offset * date_loop)
                main_end = main_start + timedelta(days=date_loop)

            if date == "week":
                new_start = start + timedelta(days=offset * 1)
                main_start = new_start.replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                main_end = new_start.replace(
                    hour=23, minute=59, second=59, microsecond=999999
                )

            if date == "year":
                main_start = start + relativedelta(months=offset)
                main_end = main_start + relativedelta(months=1)

            try:

                visit_data = get_actual_visit_data(
                    user, main_start, main_end, date_string, visit_data, date
                )

                if visit_data is None:
                    logger.error(f"Failed to get visit data for user {user.id}")
                    return Response(
                        {"error": "Failed to get visit data"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                context["visit_data"] = visit_data

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    logger.info(f"Successfully updated visit data for user {user.id}")
    return context


"""Certification Sorter"""


def get_start_date(date_filter):
    """
    Get the correct start date based on the date filter.

    Args:
        date_filter (str): The date filter, can be "week", "month", or "year".

    Returns:
        datetime: The calculated start date.
    """
    now = timezone.now()
    start = None

    if date_filter == "week":
        start = now - timedelta(days=6)
    elif date_filter == "month":
        start = now - timedelta(days=30)
    elif date_filter == "year":
        start = now - timedelta(days=365)
    else:
        logger.warning(f"Invalid date filter: {date_filter}")

    logger.info(f"Start date for date filter '{date_filter}': {start}")
    return start


def get_status(status_filter):
    """
    Get the status based on the status filter.

    Args:
        status_filter (str): The status filter, can be "all", "pending", or "released".

    Returns:
        bool or None: The corresponding status, or None if the filter is invalid or "all".
    """
    original_status_filter = status_filter

    if status_filter == "all":
        status_filter = None
    elif status_filter == "pending":
        status_filter = False
    elif status_filter == "released":
        status_filter = True
    else:
        logger.warning(f"Invalid status filter: {status_filter}")
        status_filter = None

    logger.info(
        f"Status filter '{original_status_filter}' mapped to status: {status_filter}"
    )
    return status_filter


def get_certificate_requests(date_filter, status_filter):
    """
    Get certificate requests based on date and status filters.

    Args:
        date_filter (str): The date filter, can be "week", "month", or "year".
        status_filter (str): The status filter, can be "all", "pending", or "released".

    Returns:
        QuerySet or None: The filtered certificate requests, or None if an error occurs.
    """
    status_filter = get_status(status_filter)
    start = get_start_date(date_filter)

    filters = {}
    if status_filter is not None:
        filters["released"] = status_filter
    if start is not None:
        filters["requested__gte"] = start.date()

    try:
        requests = Certificate.objects.filter(**filters).annotate(
            email=F("patient__email"),
            first_name=F("patient__first_name"),
            last_name=F("patient__last_name"),
        )
        logger.info(
            f"Certificate requests successfully retrieved with filters: {filters}"
        )
        return requests
    except Exception as e:
        logger.error(f"Error retrieving certificate requests: {e}")
        return None


"""Certificate Data"""


def get_certificate_data(status_filter, date_filter, cert_data):
    """
    Get certificate data based on status and date filters.

    Args:
        status_filter (str): Filter for certificate status ("all", "pending", "released").
        date_filter (str): Filter for the date range ("week", "month", "year").
        cert_data (dict): Dictionary to store the certificate data.

    Returns:
        dict: Updated certificate data with the counts based on the filters.
        None: If an error occurs during the retrieval.

    """
    status = status_filter
    start, max_range, date_string, date_loop = init_params(date_filter)
    status_filter = get_status(status_filter)

    for offset in range(max_range):
        try:
            # Determine the start and end dates based on the date filter
            if date_filter == "month":
                main_start = start + timedelta(days=offset * date_loop)
                main_end = main_start + timedelta(days=date_loop)
            elif date_filter == "week":
                new_start = start + timedelta(days=offset)
                main_start = new_start.replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                main_end = new_start.replace(
                    hour=23, minute=59, second=59, microsecond=999999
                )
            elif date_filter == "year":
                main_start = start + relativedelta(months=offset)
                main_end = main_start + relativedelta(months=1)
            else:
                raise ValueError(f"Invalid date filter: {date_filter}")

            # Fetch the count of certificates based on the status filter and date range
            if status_filter is None:
                count = Certificate.objects.filter(
                    requested__gte=main_start, requested__lt=main_end
                ).count()
            else:
                count = Certificate.objects.filter(
                    released=status_filter,
                    requested__gte=main_start,
                    requested__lt=main_end,
                ).count()

            logger.info(
                f"Retrieved {count} certificates for date range {main_start} to {main_end}"
            )

            # Update the certificate data
            cert_data[status][date_filter][main_start.strftime(date_string)] = (
                count or 0
            )

        except Exception as e:
            logger.error(f"Error retrieving certificate data: {e}")
            return None

    return cert_data
