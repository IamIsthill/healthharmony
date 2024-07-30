from django.shortcuts import render, redirect
# models
from users.models import User, Department
from administrator.models import Log, DataChangeLog
from django.contrib import messages

# Create your views here.
def admin_dashboard(request):
    account_checker(request)
    users = User.objects.filter(is_active = True)
    count_users = users.count() or 0
    context={'count_users':count_users}
    return render(request, 'administrator/dashboard.html', context)



def log_and_records(request):
    logs =  Log.objects.select_related('user').all()
    data_logs = DataChangeLog.objects.all()
    for log in data_logs:
        if log.old_value is None or log.old_value == {}:
            log.old_value = 'No data'
        if log.new_value is None or log.new_value == {}:
            log.new_value = 'No data'
    context = {'logs':logs, 'data_logs':data_logs}
    return render(request, 'administrator/records.html', context)

def account_view(request):
    account_checker(request)
    if request.method == 'POST':
        try:
            department, created =  Department.objects.get_or_create(department = request.POST.get('department'))
            if created:
                Log.objects.create(
                    user = request.user,
                    action = f'Created a new department instance'
                )
            user = User.objects.create(
                first_name = request.POST.get('first_name'),
                last_name = request.POST.get('last_name'),
                email = request.POST.get('email'),
                access = request.POST.get('access'),
                department = department,
            )
        except:
            messages.error(request, 'System failed to create a new user.')

    users = User.objects.all()
    departments = Department.objects.all()

    for user in users:
        if user.first_name is None:
            user.first_name = ' '
        if user.last_name is None:
            user.last_name = ' '
    context = {'users':users, 'departments':departments}
    return render(request, 'administrator/account.html', context)


def account_checker(request):
    if request.user.access < 4:
        return redirect('home')

