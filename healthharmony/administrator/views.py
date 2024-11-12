from django.shortcuts import render, redirect
import logging
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from django.core.cache import cache

# models
from healthharmony.users.models import User, Department
from healthharmony.administrator.models import Log, DataChangeLog
from django.contrib import messages

# forms
from healthharmony.administrator.forms import AdminUserCreationForm

# serializers
from healthharmony.api.serializers import UserSerializer


logger = logging.getLogger(__name__)


# Create your views here
@login_required(login_url="account_login")
def admin_dashboard(request):
    if request.user.access < 4:
        return redirect("doctor-overview")
    context = {}
    try:
        user_cache = cache.get("user_cache", {})
        users = user_cache.get("active_users")
        if not users:
            users = User.objects.filter(is_active=True).count or 0
            user_cache["active_users"] = users
            cache.set("user_cache", user_cache, timeout=120 * 60)
        context = {"count_users": users}
    except Exception as e:
        logger.info(
            f"{request.user.email} failed to fetched necessary data to load administrator overview : {str(e)}"
        )
        messages.error(request, "Failed to fetched necessary data. Please reload page.")
    context.update({"page": "Dashboard"})
    return render(request, "administrator/dashboard.html", context)


@login_required(login_url="account_login")
def log_and_records(request):
    if request.user.access < 4:
        return redirect("doctor-overview")
    context = {}
    try:
        data_cache = cache.get("data_cache", {})
        logs = data_cache.get("user_logs")
        if not logs:
            logs = Log.objects.select_related("user").all()
            data_cache["user_logs"] = logs
            cache.set("data_cache", data_cache, timeout=60 * 5)
        data_logs = data_cache.get("change_logs")
        if not data_logs:
            data_logs = DataChangeLog.objects.all()
            data_logs = get_prepared_data_logs(data_logs)
            data_cache["change_logs"] = data_logs
            cache.set("data_cache", data_cache, timeout=60 * 5)

        logs_paginator = Paginator(logs, 30)
        logs_page = request.GET.get("logs_page")

        try:
            logs_page = logs_paginator.page(logs_page)
        except PageNotAnInteger:
            logs_page = logs_paginator.page(1)
        except EmptyPage:
            logs_page = logs_paginator.page(logs_paginator.num_pages)

        data_paginator = Paginator(data_logs, 30)
        data_page = request.GET.get("data_page")

        try:
            data_page = data_paginator.page(data_page)
        except PageNotAnInteger:
            data_page = data_paginator.page(1)
        except EmptyPage:
            data_page = data_paginator.page(data_paginator.num_pages)

        context = {"logs": logs_page, "data_logs": data_page}
    except Exception as e:
        logger.info(
            f"{request.user.email} failed to fetched necessary data to load administrator logs : {str(e)}"
        )
        messages.error(request, "Failed to fetched necessary data. Please reload page.")
    context.update({"page": "Log Records"})
    return render(request, "administrator/records.html", context)


@login_required(login_url="account_login")
def account_view(request):
    if request.user.access < 4:
        return redirect("doctor-overview")

    context = {}
    if request.method == "POST":
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            form.save(request)

            # delete cache
            cache.delete("user_cache")

            return redirect("admin-accounts")
        else:
            messages.error(request, "Please correct the errors.")

    try:
        user_cache = cache.get("user_cache", {})
        users = user_cache.get("query")
        if not users:
            users = User.objects.all()
            user_cache["query"] = users
            cache.set("user_cache", user_cache, timeout=(120 * 60))

        department_cache = cache.get("department_cache", {})
        departments = department_cache.get("department")

        if not departments:
            departments = Department.objects.all()
            department_cache["query"] = departments
            cache.set("department_cache", department_cache, timeout=(120 * 60))

        # serialize users
        user_data = []
        if users:
            for user in users:
                if user.access <= 4:
                    data = UserSerializer(user)
                    user_data.append(data.data)

        user_page = account_paginate_user(request, users)

        context = {
            "users": user_page,
            "departments": departments,
            "user_data": user_data,
        }
    except Exception as e:
        logger.info(
            f"{request.user.email} failed to fetched necessary data to load administrator accounts view : {str(e)}"
        )
        messages.error(request, "Failed to fetched necessary data. Please reload page.")
    context.update({"page": "Account Management"})
    return render(request, "administrator/account.html", context)


def account_checker(request):
    if request.user.access < 4:
        return redirect("home")


def get_prepared_data_logs(data_logs):
    for log in data_logs:
        if log.old_value is None or log.old_value == {}:
            log.old_value = "No data"
        if log.new_value is None or log.new_value == {}:
            log.new_value = "No data"

    return data_logs


@login_required(login_url="account_login")
def post_update_user_access(request):
    if request.user.access < 4:
        return redirect("doctor-overview")
    if request.method.lower() == "post":
        user_id = request.POST.get("user_id")
        access = request.POST.get("access")

        try:
            user = User.objects.get(id=int(user_id))
        except Exception as e:
            logger.info(
                f"{request.user.email} tried to search for a user with a non-existing id: {str(e)}"
            )
            messages.error(request, "Failed to find the user. Please try again.")
            return redirect("admin-accounts")

        user.access = int(access)
        user.save()

        Log.objects.create(
            user=request.user,
            action=f"{request.user.email} has changed the access for user[{user.id}]",
        )
        logger.info(f"{request.user.email} has changed the access for user[{user.id}]")
        messages.success(request, f"Successfully update the access for {user.email}")

        # delete cache
        cache.delete_many(
            [
                "user_cache",
                "certificate_cache",
                "inventory_cache",
                "doctor_cache",
                "illness_cache",
            ]
        )
    return redirect("admin-accounts")


@login_required(login_url="account_login")
def post_delete_user(request):
    if request.user.access < 4:
        return redirect("doctor-overview")
    if request.method.lower() == "post":
        user_id = request.POST.get("user_id")

        try:
            user = User.objects.get(id=int(user_id))
        except Exception as e:
            logger.info(
                f"{request.user.email} tried to search for a user with a non-existing id: {str(e)}"
            )
            messages.error(request, "Failed to find user. Please try again")
            return redirect("admin-accounts")

        user.delete()

        logger.info(f"{request.user.email} has deleted user[{user.id}]")
        Log.objects.create(
            user=request.user,
            action=f"{request.user.email} has deleted user[{user.id}]",
        )
        messages.success(request, f"Successfully deleted user with email {user.email}")

        # delete cache
        cache.delete_many(
            [
                "user_cache",
                "certificate_cache",
                "inventory_cache",
                "doctor_cache",
                "illness_cache",
            ]
        )

    return redirect("admin-accounts")


def account_paginate_user(request, users):
    user_paginator = Paginator(users, 20)
    page = request.GET.get("page")

    try:
        user_page = user_paginator.page(page)
    except PageNotAnInteger:
        user_page = user_paginator.page(1)
    except EmptyPage:
        user_page = user_paginator.page(user_paginator.num_pages)
    return user_page
