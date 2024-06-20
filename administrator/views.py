from django.shortcuts import render
# models
from django.contrib.auth.models import User

# Create your views here.
def admin_dashboard(request):
    users = User.objects.all()
    count_users = users.count()
    context={'count_users':count_users}
    return render(request, 'administrator/dashboard.html', context)
