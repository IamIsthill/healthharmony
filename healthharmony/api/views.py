from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from django.db.models import F, Count, Prefetch, Q
from collections import defaultdict
import logging

from healthharmony.models.bed.models import BedStat
from healthharmony.models.treatment.models import Certificate, Illness, Category
from healthharmony.users.models import User, Department

from healthharmony.api.serializers import BedStatSerializer, CertificateSerializer

from healthharmony.api.functions import (
    update_context_visit_data,
    get_certificate_requests,
    get_certificate_data,
)


logger = logging.getLogger(__name__)


# Create your views here.
@api_view(["GET"])
def get_user_illness_count(request):
    email = request.query_params.get("email", None)
    if not email:
        return Response(
            {"Error": "Related data not fetched"}, status=status.HTTP_400_BAD_REQUEST
        )

    illness_count = defaultdict(lambda: defaultdict(int))
    labels = defaultdict(int)
    now = timezone.now()
    date_filter = ["week", "month", "year"]
    context = {}

    for date in date_filter:
        if date == "week":
            start = now - timedelta(days=6)
        elif date == "month":
            start = now - timedelta(days=30)
        elif date == "year":
            start = now - timedelta(days=365)
        else:
            start = None

        try:
            user = User.objects.get(email=email)
            categories = Category.objects.annotate(
                illness_count=Count(
                    "illness_category",
                    filter=Q(
                        illness_category__patient=user,
                        illness_category__updated__gte=start,
                        illness_category__updated__lt=now,
                    ),
                )
            ).filter(illness_count__gt=0)

            for cat in categories:
                illness_count[date][cat.id] = cat.illness_count or 0
                labels[cat.id] = cat.category
            context.update({"illness_count": illness_count, "labels": labels})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse(context)


@api_view(["GET"])
def get_visit_data(request):
    context = {}
    email = request.query_params.get("email", None)

    if email:
        try:

            user = User.objects.get(email=email)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"error": "please login"}, status=status.HTTP_400_BAD_REQUEST)

    context = update_context_visit_data(user, context)

    return JsonResponse(context)


@api_view(["GET"])
def get_session_email(request):
    email = request.session.get("email")
    context = {"email": email}
    return JsonResponse(context)


@api_view(["GET"])
def api_data(request):
    beds = BedStat.objects.all()
    serializer = BedStatSerializer(beds, many=True)
    return Response(serializer.data)
    # return JsonResponse(serializer.data, safe=True)


@api_view(["GET"])
def certificate_sorter(request):
    """
    Retrieve sorted certificate requests based on status and date filters.

    Query Parameters:
    - status_filter (str): The status filter, can be "all", "pending", or "released".
    - date_filter (str): The date filter, can be "week", "month", or "year".

    Returns:
    - Response: A JSON response containing the sorted certificate requests or an error message.
    """
    status_filter = request.query_params.get("status_filter", "all")
    date_filter = request.query_params.get("date_filter", "week")

    try:
        logger.info(
            f"Retrieving certificate requests with status_filter='{status_filter}' and date_filter='{date_filter}'"
        )
        requests = get_certificate_requests(date_filter, status_filter)

        if requests is None:
            raise ValueError("Failed to retrieve certificate requests.")

        serializer = CertificateSerializer(requests, many=True)
        logger.info("Certificate requests successfully retrieved and serialized.")
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error in certificate_sorter: {e}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def certificate_data(request):
    """
    API endpoint to retrieve certificate data based on status and date filters.

    Args:
        request (HttpRequest): The request object containing query parameters for filters.

    Query Parameters:
        status_filter (str): Filter for certificate status ("all", "pending", "released"). Default is "all".
        date_filter (str): Filter for the date range ("week", "month", "year"). Default is "week".

    Returns:
        JsonResponse: JSON response with the certificate data or an error message.
    """
    status_filter = request.query_params.get("status_filter", "all")
    date_filter = request.query_params.get("date_filter", "week")
    cert_data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    try:
        cert_data = get_certificate_data(status_filter, date_filter, cert_data)
        if cert_data is None:
            logger.error("Failed to retrieve certificate data.")
            return Response(
                {"error": "Failed to retrieve certificate data."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return JsonResponse(cert_data)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def user_data(request):
    now = timezone.now()
    date_filter = request.query_params.get("date_filter", "year")
    users = defaultdict(lambda: defaultdict(int))

    if date_filter == "week":
        start = now - timedelta(days=6)
        max_range = 7
        date_string = "%A, %d"
        date_loop = 1
    elif date_filter == "month":
        start = now - timedelta(days=30)
        max_range = 6
        date_string = "%B, %d"
        date_loop = 5

    elif date_filter == "year":
        start = now - timedelta(days=365)
        max_range = 12
        date_string = "%B"
        date_loop = 1
    else:
        start = None

    for offset in range(max_range):
        if date_filter == "month":
            main_start = start + timedelta(days=offset * date_loop)
            main_end = main_start + timedelta(days=date_loop)

        if date_filter == "week":
            new_start = start + timedelta(days=offset * 1)
            main_start = new_start.replace(hour=0, minute=0, second=0, microsecond=0)
            main_end = new_start.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )

        if date_filter == "year":
            main_start = start + relativedelta(months=offset)
            main_end = main_start + relativedelta(months=1)

        count = User.objects.filter(
            date_joined__gte=main_start, date_joined__lt=main_end
        ).count()
        users[date_filter][main_start.strftime(date_string)] = count or 0

    return JsonResponse(users)


@api_view(["GET"])
def account_roles(request):
    patients = User.objects.filter(access=1).count() or 0
    staffs = User.objects.filter(access=2).count() or 0
    doctors = User.objects.filter(access=3).count() or 0
    data = {"patient": patients, "staff": staffs, "doctor": doctors}
    return JsonResponse(data)


@api_view(["GET"])
def user_demographics(request):
    departments = Department.objects.annotate(user_count=Count("user_department"))
    # Create a list of dictionaries to serialize to JSON
    department_list = [
        {"department": department.department, "user_count": department.user_count or 0}
        for department in departments
    ]
    return JsonResponse(department_list, safe=False)


@api_view(["GET"])
def filtered_account_list(request):
    access = request.GET.get("access", "all")

    access_map = {"patient": 1, "staff": 2, "doctor": 3}

    reverse_access_map = {v: k for k, v in access_map.items()}

    if access == "all":
        users = User.objects.values(
            "first_name", "last_name", "email", "date_joined", "access"
        )
    else:
        access_value = access_map.get(access)
        if access_value is not None:
            users = User.objects.filter(access=access_value).values(
                "first_name", "last_name", "email", "date_joined", "access"
            )
        else:
            return JsonResponse({"error": "Invalid access type"}, status=400)

    users_list = list(users)  # Convert ValuesQuerySet to a list
    for user in users_list:
        if user["first_name"] is None:
            user["first_name"] = " "
        if user["last_name"] is None:
            user["last_name"] = " "
        user["access"] = reverse_access_map.get(user["access"], "unknown")

    return JsonResponse(users_list, safe=False)
