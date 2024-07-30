from django.shortcuts import render, redirect
import logging

# models
from healthharmony.users.models import User, Department
from healthharmony.administrator.models import Log, DataChangeLog
from django.contrib import messages


logger = logging.getLogger(__name__)


# Create your views here
def admin_dashboard(request):
    account_checker(request)
    users = User.objects.filter(is_active=True)
    count_users = users.count() or 0
    context = {"count_users": count_users}
    return render(request, "administrator/dashboard.html", context)


def log_and_records(request):
    logs = Log.objects.select_related("user").all()
    data_logs = DataChangeLog.objects.all()
    for log in data_logs:
        if log.old_value is None or log.old_value == {}:
            log.old_value = "No data"
        if log.new_value is None or log.new_value == {}:
            log.new_value = "No data"
    context = {"logs": logs, "data_logs": data_logs}
    return render(request, "administrator/records.html", context)


def account_view(request):
    account_checker(request)
    if request.method == "POST":
        try:
            department_name = request.POST.get("department")
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            email = request.POST.get("email")
            access = request.POST.get("access")

            if not (department_name and first_name and last_name and email and access):
                raise ValueError("Missing required fields")

            department, created = Department.objects.get_or_create(
                department=department_name
            )
            if created:
                Log.objects.create(
                    user=request.user, action="Created a new department instance"
                )

            user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                access=access,
                department=department,
            )
            messages.success(request, "User created successfully.")
        except ValueError as ve:
            messages.error(request, f"Input error: {ve}")
            logger.error(f"Input error: {ve}")
        except Department.DoesNotExist:
            messages.error(request, "Department does not exist.")
            logger.error("Department does not exist.")
        except User.DoesNotExist:
            messages.error(request, "User creation failed due to a related error.")
            logger.error("User creation failed due to a related error.")
        except Exception as e:
            messages.error(request, "System failed to create a new user.")
            logger.error(f"Unexpected error: {e}")

    users = User.objects.all()
    departments = Department.objects.all()

    for user in users:
        if user.first_name is None:
            user.first_name = " "
        if user.last_name is None:
            user.last_name = " "
    context = {"users": users, "departments": departments}
    return render(request, "administrator/account.html", context)


def account_checker(request):
    if request.user.access < 4:
        return redirect("home")
