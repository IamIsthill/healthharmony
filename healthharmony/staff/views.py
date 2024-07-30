from django.shortcuts import render, redirect
from healthharmony.users.models import User, Department
from healthharmony.staff.forms import PatientForm
import secrets
import string
from healthharmony.treatment.models import Illness, Certificate, Category
from healthharmony.inventory.models import InventoryDetail, QuantityHistory
from healthharmony.administrator.models import Log, DataChangeLog
from healthharmony.bed.models import BedStat
from django.db.models import Sum, F, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
import json
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from django.core.mail import EmailMessage
import environ
env = environ.Env()
environ.Env.read_env()

def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for i in range(length))

def add_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        email = request.POST.get('email')
        user = User.objects.get(email = email)
        if user:
            messages.error(request, 'User already exists')
            return redirect('register')
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(generate_password())
            user.backend = 'django.contrib.auth.backends.ModelBackend'  # Specify the backend
            user.save()
            # login(request, user)
            return redirect('home')  # Redirect to the home page or another appropriate URL
    else:
        form = PatientForm()
    
    return render(request, 'staff/add-patient.html', {'form': form})

def overview(request):
    access_checker(request)
    now = timezone.now()
    start_date = (now - timedelta(days=365)).replace(day=1)
    today_patient = Illness.objects.filter(updated__date = now.date()).count()
    total_patient = Illness.objects.all().count()
    monthly_medcert = Certificate.objects.filter(requested__month = now.month,requested__year = now.year, released = True).count()
    categories = Category.objects.all()
    category_data = defaultdict(lambda: defaultdict(int))
    category_data['categories'] = json.dumps(list(categories.values('id', 'category')))
    departments = Department.objects.all()
    departments_names = Department.objects.all().values('id', 'department')
    department_data = defaultdict(lambda: defaultdict(int))

    for department in departments:
        year_cases = []
        department_data['yearly_count'][department.id] = 0
        department_data['monthly_count'][department.id] = 0
        department_data['weekly_count'][department.id] = 0
        for month_offset in range(13): 
            current_month = start_date + relativedelta(months=month_offset)
            next_month = current_month + relativedelta(months=1)
            if month_offset == 12:  
                patient_count = User.objects.filter(
                    department=department,
                    date_joined__gte=current_month,
                    date_joined__lte=now 
                ).count()
            else:
                patient_count = User.objects.filter(
                    department=department,
                    date_joined__gte=current_month,
                    date_joined__lt=next_month
                ).count()
            year_cases.append((current_month.strftime('%B'), patient_count))
            department_data['yearly'][department.id]=json.dumps(year_cases)
            department_data['yearly_count'][department.id] += patient_count
        
        five_days_count = []
        last30days = (now - timedelta(days=30))
        for five_offset in range(6):
            current_day = last30days + timedelta(days=five_offset*5)
            next_five = current_day + timedelta(days=5)
            patient_count = User.objects.filter(
                    department=department,
                    date_joined__gte=current_day,
                    date_joined__lt=next_five 
            ).count()
            five_days_count.append((current_day.strftime('%B %d'), patient_count))
            department_data['monthly'][department.id]=json.dumps(five_days_count)
            department_data['monthly_count'][department.id] += patient_count


        weekly_count = []
        week = now - timedelta(days=6)
        for day_offset in range(7):
            current_day = week + timedelta(days = day_offset*1)
            start_of_day = current_day.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = current_day.replace(hour=23, minute=59, second=59, microsecond=999999)
            patient_count = User.objects.filter(
                    department=department,
                    date_joined__gte=start_of_day,
                    date_joined__lte=end_of_day,
            ).count()
            weekly_count.append((current_day.strftime('%A, %d'), patient_count))
            department_data['weekly'][department.id]=json.dumps(weekly_count)
            department_data['weekly_count'][department.id] += patient_count
        
    # category_counts = []

    for category in categories:
        month_cases = []
        category_data['yearly_count'][category.id] = 0
        category_data['monthly_count'][category.id] = 0
        category_data['weekly_count'][category.id] = 0

        for month_offset in range(13):  # 13 months to include the current month
            current_month = start_date + relativedelta(months=month_offset)
            next_month = current_month + relativedelta(months=1)
            if month_offset == 12:  
                illness_count = Illness.objects.filter(
                    illness_category=category,
                    updated__gte=current_month,
                    updated__lte=now 
                ).count()
            else:
                illness_count = Illness.objects.filter(
                    illness_category=category,
                    updated__gte=current_month,
                    updated__lt=next_month
                ).count()
            month_cases.append((current_month.strftime('%B'), illness_count))
            category_data['yearly'][category.id]=json.dumps(month_cases)
            category_data['yearly_count'][category.id] += illness_count

        five_days_count = []
        last30days = (now - timedelta(days=30))
        for five_offset in range(6):
            current_day = last30days + timedelta(days=five_offset*5)
            next_five = current_day + timedelta(days=5)
            illness_count = Illness.objects.filter(
                    illness_category=category,
                    updated__gte=current_day,
                    updated__lt=next_five 
            ).count()
            five_days_count.append((current_day.strftime('%B %d'), illness_count))
            category_data['monthly'][category.id]=json.dumps(five_days_count)
            category_data['monthly_count'][category.id] += illness_count
        
        weekly_count = []
        week = now - timedelta(days=6)
        for day_offset in range(7):
            current_day = week + timedelta(days = day_offset*1)
            start_of_day = current_day.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = current_day.replace(hour=23, minute=59, second=59, microsecond=999999)
            illness_count = Illness.objects.filter(
                    illness_category=category,
                    updated__gte=start_of_day,
                    updated__lte=end_of_day,
            ).count()
            weekly_count.append((current_day.strftime('%A, %d'), illness_count))
            category_data['weekly'][category.id]=json.dumps(weekly_count)
            category_data['weekly_count'][category.id] += illness_count

    

    context = {'page': 'overview', 'today_patient' : today_patient, 'monthly_medcert':monthly_medcert, 'categories':categories, 'category_data':category_data, 'total_patient':total_patient, 'department_data':department_data, 'departments':list(departments_names)}
    return render(request, 'staff/overview.html', context)

def add_issue(request):
    patients = User.objects.filter(access=1)
    if request.method == 'POST':
        patient = User.objects.get(email=request.POST.get('patient'))
        try:
            illness = Illness.objects.create(
                patient = patient,
                issue = request.POST.get('issue'),
            )
            logs = Log.objects.create(
                user = request.user,
                action = "Added a new illness"
            )
        except:
            messages.error(request, 'Unable to add issue')
    context = {'patients':patients}
    return render(request,'staff/add-issue.html', context)

def inventory(request):
    access_checker(request)
    now = timezone.now()
    counts = {'medicine_avail': 0, 'medicine_expired': 0, 'supply_avail': 0, 'supply_expired': 0}  
    inventory = InventoryDetail.objects.all().annotate(total_quantity=Sum('quantities__updated_quantity')).values('id', 'item_name', 'category', 'expiration_date', 'total_quantity')
    inventory_data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for inv in inventory:
        if inv['total_quantity'] is None:
            inv['total_quantity'] = 0
        if inv['category'] == 'Medicine' and inv['expiration_date'] > now.date():
            counts['medicine_avail'] += inv['total_quantity']
        if inv['category'] == 'Medicine' and inv['expiration_date'] <= now.date():
            counts['medicine_expired'] += inv['total_quantity']
        if inv['category'] == 'Supply' and inv['expiration_date'] > now.date() or inv['expiration_date'] is None:
            counts['supply_avail'] += inv['total_quantity']
        if inv['category'] == 'Supply' and inv['expiration_date'] <= now.date():
            counts['supply_expired'] += inv['total_quantity']
    
    start_date = (now - timedelta(days=365)).replace(day=1)
    for month_offset in range(13):
        current_month = start_date + relativedelta(months=month_offset)
        next_month = current_month + relativedelta(months=1)
        inventory_data['medicine']['year'][current_month.strftime('%B')] = 0
        inventory_data['supply']['year'][current_month.strftime('%B')] = 0
        inventory_data['medicine']['detail-year'][inv['item_name']] = 0
        inventory_data['supply']['detail-year'][inv['item_name']] = 0

        for inv in inventory:
            item_data = InventoryDetail.objects.get(pk = inv['id'])
            item_data_quantity = item_data.quantities.filter(timestamp__gte = current_month, timestamp__lt = next_month).aggregate(total_quantity=Sum('updated_quantity'))
            if inv['category'] == 'Medicine' and inv['expiration_date'] >= current_month.date() and inv['expiration_date'] < next_month.date():
                inventory_data['medicine']['year'][current_month.strftime('%B')] += inv['total_quantity']
            elif inv['category'] == 'Supply' and inv['expiration_date'] >= current_month.date() and inv['expiration_date'] < next_month.date():
                inventory_data['supply']['year'][current_month.strftime('%B')] += inv['total_quantity']
            if inv['category'] == 'Medicine':
                inventory_data['medicine']['detail-year'][inv['item_name']] = item_data_quantity['total_quantity'] or 0
            if inv['category'] == 'Supply':
                inventory_data['supply']['detail-year'][inv['item_name']] = item_data_quantity['total_quantity'] or 0


    last30days = (now - timedelta(days=30))
    for five_offset in range(6):
        current_day = last30days + timedelta(days=five_offset*5)
        next_five = current_day + timedelta(days=5)
        inventory_data['medicine']['month'][current_day.strftime('%B %d')] = 0
        inventory_data['supply']['month'][current_day.strftime('%B %d')] = 0


        for inv in inventory:
            item_data = InventoryDetail.objects.get(pk = inv['id'])
            item_data_quantity = item_data.quantities.filter(timestamp__gte = current_day, timestamp__lt = next_five).aggregate(total_quantity=Sum('updated_quantity'))
            if inv['category'] == 'Medicine' and inv['expiration_date'] >= current_day.date() and inv['expiration_date'] < next_five.date():
                inventory_data['medicine']['month'][current_day.strftime('%B %d')] += inv['total_quantity']
            elif inv['category'] == 'Supply' and inv['expiration_date'] >= current_day.date() and inv['expiration_date'] < next_five.date():
                inventory_data['supply']['month'][current_day.strftime('%B %d')] += inv['total_quantity']
            if inv['category'] == 'Medicine':
                inventory_data['medicine']['detail-month'][inv['item_name']] = item_data_quantity['total_quantity'] or 0
            if inv['category'] == 'Supply':
                inventory_data['supply']['detail-month'][inv['item_name']] = item_data_quantity['total_quantity'] or 0
                
    week = now - timedelta(days=6)
    for day_offset in range(7):
        current_day = week + timedelta(days = day_offset*1)
        start_of_day = current_day.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = current_day.replace(hour=23, minute=59, second=59, microsecond=999999)

        inventory_data['medicine']['week'][start_of_day.strftime('%B %d')] = 0
        inventory_data['supply']['week'][start_of_day.strftime('%B %d')] = 0

        for inv in inventory:
            item_data = InventoryDetail.objects.get(pk = inv['id'])
            item_data_quantity = item_data.quantities.filter(timestamp__gte = start_of_day, timestamp__lt = end_of_day).aggregate(total_quantity=Sum('updated_quantity'))
            if inv['category'] == 'Medicine' and inv['expiration_date'] >= start_of_day.date() and inv['expiration_date'] < end_of_day.date():
                inventory_data['medicine']['week'][start_of_day.strftime('%B %d')] += inv['total_quantity']
            elif inv['category'] == 'Supply' and inv['expiration_date'] >= start_of_day.date() and inv['expiration_date'] < end_of_day.date():
                inventory_data['supply']['week'][current_day.strftime('%B %d')] += inv['total_quantity']
            if inv['category'] == 'Medicine':
                inventory_data['medicine']['detail-week'][inv['item_name']] = item_data_quantity['total_quantity'] or 0
            if inv['category'] == 'Supply':
                inventory_data['supply']['detail-week'][inv['item_name']] = item_data_quantity['total_quantity'] or 0
        
    inventory_list = list(inventory)

    
    context = {'page': 'inventory', 'inventory': inventory_list,'counts': counts, 'inventory_data': dict(inventory_data)}
    return render(request, 'staff/inventory.html', context)

def add_inventory(request):
    if request.method == 'POST':
        try:
            item = InventoryDetail.objects.create(
                item_no = request.POST.get('item_no'),
                unit = request.POST.get('unit'),
                item_name = request.POST.get('item_name'),
                category = request.POST.get('category'),
                description = request.POST.get('description'),
                expiration_date = request.POST.get('expiration_date')
            )
            Log.objects.create(
                user = request.user,
                action = f'Created inventory item with id [{item.id}]'
            )
            return redirect('staff-inventory')
        except:
            messages.error(request, 'Failed to add the inventory item')

def bed(request):
    access_checker(request)
    try:
        beds = BedStat.objects.all()
    except Exception as e:
        messages.error(request, 'Error fetching bed data')
    context = {'beds':beds, 'page': 'bed'}
    return render(request, 'staff/bed.html', context)

def bed_handler(request, pk):
    access_checker(request)
    if request.method == 'POST':
        try:
            bed = BedStat.objects.get(id=pk)
            bed.status = not bed.status
            bed.save()
            Log.objects.create(
                user = request.user,
                action=f'Updated BedStat({bed.id}) from {not bed.status} to {bed.status}'
            )
            messages.success(request, 'Bed was successfully updated')
        except Exception as e:
            messages.error(request, 'Error fetching bed data')
    return redirect('staff-bed')

def records(request):
    access_checker(request)
    email = env('EMAIL_ADD')
    now = timezone.now()
    context = {'page':'records', 'email':email}
    try:
        requests = Certificate.objects.all()
        history = Illness.objects.all().annotate(first_name=Coalesce(F('patient__first_name'), Value('')),
        last_name=Coalesce(F('patient__last_name'), Value('')))
        context.update({
            'history':history
        })
    except Exception as e:
        messages.error(request, 'Error fetching data')
    return render(request, 'staff/records.html', context)



def create_patient_add_issue(request):
    access_checker(request)
    if request.method == 'POST':
        try:
            patient, created = User.objects.get_or_create(email = request.POST.get('email'))
            if created:
                patient.access = 1
                password = generate_password()
                patient.set_password(password)
                patient.save()
                logs = Log.objects.create(
                    user = request.user,
                    action = f'Created new user {patient.email} with id [{patient.id}]'
                )
                subject = 'Welcome New User'
                body = f'<h1>This is your password {password}</h1><p>With HTML content</p>'
                from_email = env('EMAIL_ADD')
                recipient_list = [patient.email]
                email = EmailMessage(subject, body, from_email, recipient_list)
                email.content_subtype = 'html' 
                email.send()
            visit = Illness.objects.create(
                patient = patient,
                issue = request.POST.get('issue')
            )
            DataChangeLog.objects.create(
                table='Illness',
                record_id = visit.id,
                action = 'create',
                new_value = visit.__str__(),
                changed_by = request.user,
            )

        except:
            messages.error(request, 'System faced some error')
        return redirect('staff-records')

def access_checker(request):
    if request.user.access < 2:
        return redirect('home')



