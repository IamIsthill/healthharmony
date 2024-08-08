from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import logging

from healthharmony.treatment.models import Category, Illness


logger = logging.getLogger(__name__)


def getCategory(request):
    try:
        categories = Category.objects.all()
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        messages.error(request, "Error fetching data. Please reload.")
    return categories, request


def sort_category(categories, request):
    category_data = {}
    data_filter = ["yearly", "monthly", "weekly"]

    now = timezone.now()

    for filter in data_filter:
        if filter == "yearly":
            max_range = 12
            start = now - relativedelta(months=11)
            date_loop = 1
            date_format = "%B"

        if filter == "monthly":
            max_range = 6
            start = now - timedelta(days=30)
            date_loop = 5
            date_format = "%B %d"

        if filter == "weekly":
            start = now - timedelta(days=6)
            max_range = 7
            date_format = "%A, %d"
            date_loop = 1

        for offset in range(max_range):
            if filter == "yearly":
                main_start = start + relativedelta(months=offset, day=1)
                main_end = main_start + relativedelta(months=date_loop)

            if filter == "monthly":
                main_start = start + timedelta(days=offset * date_loop)
                main_end = main_start + timedelta(days=date_loop)

            if filter == "weekly":
                new_start = start + timedelta(days=offset * date_loop)
                main_start = new_start.replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                main_end = new_start.replace(
                    hour=23, minute=59, second=59, microsecond=999999
                )

            request, category_data = sort_category_loop(
                categories,
                main_start,
                main_end,
                category_data,
                date_format,
                request,
                filter,
            )

    return request, category_data


def sort_category_loop(
    categories, main_start, main_end, category_storage, date_format, request, filter
):
    for category in categories:
        try:
            illnesses = Illness.objects.select_related("illness_category").filter(
                illness_category=category, updated__gte=main_start, updated__lt=main_end
            )

            if filter == "weekly":
                illnesses = Illness.objects.filter(
                    illness_category=category,
                    updated__gte=main_start,
                    updated__lte=main_end,
                )

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

            if illnesses:
                category_storage[filter][category.id][category.category][
                    main_start.strftime(date_format)
                ] = [illness_to_dict(illness) for illness in illnesses]

        except Exception as e:
            logger.error(f"Failed to sort data: {str(e)}")
            messages.error(request, "Failed to sort data. Please try again")

    return request, category_storage


def illness_to_dict(illness):
    return {
        "id": illness.id,
        "issue": illness.issue,
        "category_id": illness.illness_category.id,
        "category": illness.illness_category.category,
    }


def get_sorted_category(request):
    categories, request = getCategory(request)

    if categories is None:
        return request, categories

    request, category_data = sort_category(categories, request)

    return request, category_data
