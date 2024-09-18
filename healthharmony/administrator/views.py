from django.shortcuts import render, redirect
import logging
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required

# models
from healthharmony.users.models import User, Department
from healthharmony.administrator.models import Log, DataChangeLog
from django.contrib import messages


# forms
from healthharmony.administrator.forms import AdminUserCreationForm


logger = logging.getLogger(__name__)


# Create your views here
@login_required(login_url="account_login")
def admin_dashboard(request):
    account_checker(request)
    context = {}
    try:
        users = User.objects.filter(is_active=True)
        count_users = users.count() or 0
        context = {"count_users": count_users}
    except Exception as e:
        logger.info(
            f"{request.user.email} failed to fetched necessary data to load administrator overview : {str(e)}"
        )
        messages.error(request, "Failed to fetched necessary data. Please reload page.")
    return render(request, "administrator/dashboard.html", context)


@login_required(login_url="account_login")
def log_and_records(request):
    account_checker(request)
    context = {}
    try:
        logs = Log.objects.select_related("user").all()
        data_logs = DataChangeLog.objects.all()
        data_logs = get_prepared_data_logs(data_logs)

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
    return render(request, "administrator/records.html", context)


@login_required(login_url="account_login")
def account_view(request):
    account_checker(request)
    context = {}
    if request.method == "POST":
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(request)
            return redirect("admin-accounts")
        else:
            messages.error(request, "Please correct the errors.")

    try:
        users = User.objects.all()
        departments = Department.objects.all()

        for user in users:
            if user.first_name is None:
                user.first_name = " "
            if user.last_name is None:
                user.last_name = " "
        context = {"users": users, "departments": departments}
    except Exception as e:
        logger.info(
            f"{request.user.email} failed to fetched necessary data to load administrator accounts view : {str(e)}"
        )
        messages.error(request, "Failed to fetched necessary data. Please reload page.")
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
