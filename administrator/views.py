from django.shortcuts import render, redirect
# models
from users.models import User

# Create your views here.
def admin_dashboard(request):
    account_checker(request)
    users = User.objects.filter(is_active = True)
    count_users = users.count() or 0
    context={'count_users':count_users}
    return render(request, 'administrator/dashboard.html', context)

def account_checker(request):
    if request.user.access < 4:
        return redirect('home')
