from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from django.db.models import F, Count, Prefetch, Q
from collections import defaultdict

from bed.models import BedStat
from treatment.models import Certificate, Illness, Category
from users.models import User, Department

from api.serializers import BedStatSerializer, CertificateSerializer


# Create your views here.
@api_view(['GET'])
def get_user_illness_count(request):
    email = request.query_params.get('email', None)
    if not email:
        return Response({'Error': 'Related data not fetched'}, status=status.HTTP_400_BAD_REQUEST)
    
    illness_count = defaultdict(lambda: defaultdict(int))
    labels = defaultdict(int)
    now = timezone.now()
    date_filter = ['week', 'month', 'year']
    context = {}

    for date in date_filter:
        if date == 'week':
            start = now - timedelta(days = 6)
            max_range = 7
            date_string = '%A, %d'
            date_loop = 1
        elif date == 'month':
            start = now - timedelta(days = 30)
            max_range = 6
            date_string = '%B, %d'
            date_loop = 5
        elif date == 'year':
            start = now - timedelta(days = 365)
            max_range = 13
            date_string = '%B'
            date_loop = 1
        else:
            start = None 
        
        

        try:
            user = User.objects.get(email = email)
            categories = Category.objects.annotate(
                illness_count=Count(
                    'illness_category',
                    filter=Q(illness_category__patient=user, illness_category__updated__gte=start, illness_category__updated__lt=now)
                )
            ).filter(illness_count__gt=0)

            for cat in categories:
                illness_count[date][cat.id] = cat.illness_count or 0
                labels[cat.id] = cat.category
            context.update({
                'illness_count': illness_count,
                'labels': labels
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse(context)


@api_view(['GET'])
def get_visit_data(request):
    visit_data = defaultdict(lambda: defaultdict(int))
    context = {}
    email = request.query_params.get('email', None)

    if email:
        try:

            visits =Illness.objects.filter( patient__email = str(email) )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        visits = Illness.objects.all().values('added')


    #temporary
    visits = Illness.objects.filter(patient__id = 40).values('added')
    
    now = timezone.now()

    date_filter = ['week', 'month', 'year']

    for date in date_filter:
        if date == 'week':
            start = now - timedelta(days = 6)
            max_range = 7
            date_string = '%A, %d'
            date_loop = 1
        elif date == 'month':
            start = now - timedelta(days = 30)
            max_range = 6
            date_string = '%B, %d'
            date_loop = 5
        elif date == 'year':
            start = now - timedelta(days = 365)
            max_range = 13
            date_string = '%B'
            date_loop = 1
        else:
            start = None 
        
        for offset in range(max_range):
            if date == 'month':
                main_start = start + timedelta(days = offset * date_loop)
                main_end = main_start + timedelta(days = date_loop)

            if date == 'week':
                new_start = start + timedelta(days = offset*1)
                main_start = new_start.replace(hour=0, minute=0, second=0, microsecond=0)
                main_end = new_start.replace(hour=23, minute=59, second=59, microsecond=999999)

            if date == 'year':
                main_start = start + relativedelta(months = offset)
                main_end = main_start + relativedelta(months=1)          

            try:
                count = Illness.objects.filter(added__gte=main_start, added__lt=main_end).count()
                visit_data[date][main_start.strftime(date_string)] = count or 0

                context.update({
                    'visit_data': visit_data
                })

            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return JsonResponse(context)



@api_view(['GET'])
def get_session_email(request):
    email = request.session.get('email')
    context = {
        'email':email
    }
    return JsonResponse(context)

@api_view(['GET'])
def api_data(request):
    beds = BedStat.objects.all()
    serializer = BedStatSerializer(beds, many=True)
    return Response(serializer.data)
    # return JsonResponse(serializer.data, safe=True)

@api_view(['GET'])
def certificate_sorter(request):
    now = timezone.now()
    status_filter = request.query_params.get('status_filter', 'all')
    date_filter = request.query_params.get('date_filter', 'week')
    if date_filter == 'week':
        start = now - timedelta(days=6)
    elif date_filter == 'month':
        start = now - timedelta(days=30)
    elif date_filter == 'year':
        start = now - timedelta(days=365)
    else:
        start = None  
    
    
    if status_filter == 'all':
        status_filter = None
    elif status_filter == 'pending':
        status_filter = False
    elif status_filter == 'released':
        status_filter = True
    else:
        status_filter = None
    try:
        filters = {}
        if status_filter is not None:
            filters['released'] = status_filter
        if start is not None:
            filters['requested__gte'] = start.date()

        requests = Certificate.objects.filter(**filters).annotate(email = F('patient__email'), first_name = F('patient__first_name'), last_name = F('patient__last_name'))
        serializer = CertificateSerializer(requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def certificate_data(request):
    now = timezone.now()
    status_filter = request.query_params.get('status_filter', 'all')
    date_filter = request.query_params.get('date_filter', 'week')
    cert_data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    status = status_filter

    if date_filter == 'week':
        start = now - timedelta(days = 6)
        max_range = 7
        date_string = '%A, %d'
        date_loop = 1
    elif date_filter == 'month':
        start = now - timedelta(days=30)
        max_range = 6
        date_string = '%B, %d'
        date_loop = 5
        
    elif date_filter == 'year':
        start = now - timedelta(days=365)
        max_range = 13
        date_string = '%B'
        date_loop = 1
    else:
        start = None  

    if status_filter == 'all':
        status_filter = None
    elif status_filter == 'pending':
        status_filter = False
    elif status_filter == 'released':
        status_filter = True
    else:
        status_filter = 'all'

    for offset in range(max_range):
        if date_filter == 'month':
            main_start = start + timedelta(days = offset * date_loop)
            main_end = main_start + timedelta(days = date_loop)

        if date_filter == 'week':
            new_start = start + timedelta(days = offset*1)
            main_start = new_start.replace(hour=0, minute=0, second=0, microsecond=0)
            main_end = new_start.replace(hour=23, minute=59, second=59, microsecond=999999)

        if date_filter == 'year':
            main_start = start + relativedelta(months = offset)
            main_end = main_start + relativedelta(months=1)

        if status_filter is None:
            count = Certificate.objects.filter(requested__gte=main_start, requested__lt=main_end).count()
        else:
            count = Certificate.objects.filter(released=status_filter, requested__gte=main_start, requested__lt=main_end).count()

        cert_data[status][date_filter][main_start.strftime(date_string)] = count or 0

    return JsonResponse(cert_data)
    
@api_view(['GET'])
def user_data(request):
    now = timezone.now()
    date_filter = request.query_params.get('date_filter', 'year')
    users = defaultdict(lambda: defaultdict(int))

    if date_filter == 'week':
        start = now - timedelta(days = 6)
        max_range = 7
        date_string = '%A, %d'
        date_loop = 1
    elif date_filter == 'month':
        start = now - timedelta(days=30)
        max_range = 6
        date_string = '%B, %d'
        date_loop = 5
        
    elif date_filter == 'year':
        start = now - timedelta(days=365)
        max_range = 12
        date_string = '%B'
        date_loop = 1
    else:
        start = None
    
    for offset in range(max_range):
        if date_filter == 'month':
            main_start = start + timedelta(days = offset * date_loop)
            main_end = main_start + timedelta(days = date_loop)

        if date_filter == 'week':
            new_start = start + timedelta(days = offset*1)
            main_start = new_start.replace(hour=0, minute=0, second=0, microsecond=0)
            main_end = new_start.replace(hour=23, minute=59, second=59, microsecond=999999)

        if date_filter == 'year':
            main_start = start + relativedelta(months = offset)
            main_end = main_start + relativedelta(months=1)

        count = User.objects.filter(date_joined__gte = main_start, date_joined__lt = main_end).count()
        users[date_filter][main_start.strftime(date_string)] = count or 0
    
    return JsonResponse(users)

@api_view(['GET'])
def account_roles(request):
    patients = User.objects.filter(access = 1).count() or 0
    staffs =  User.objects.filter(access = 2).count() or 0
    doctors =  User.objects.filter(access = 3).count() or 0
    data = {'patient' : patients, 'staff' :staffs, 'doctor': doctors}
    return JsonResponse(data)

@api_view(['GET'])
def user_demographics(request):
    departments = Department.objects.annotate(user_count=Count('user_department'))
    # Create a list of dictionaries to serialize to JSON
    department_list = [
        {
            'department': department.department,
            'user_count': department.user_count or 0
        }
        for department in departments
    ]
    return JsonResponse(department_list, safe=False)

@api_view(['GET'])
def filtered_account_list(request):
    access = request.GET.get('access', 'all')

    access_map = {
        'patient': 1,
        'staff': 2,
        'doctor': 3
    }

    reverse_access_map = {v: k for k, v in access_map.items()}

    if access == 'all':
        users = User.objects.values('first_name', 'last_name', 'email', 'date_joined', 'access')
    else:
        access_value = access_map.get(access)
        if access_value is not None:
            users = User.objects.filter(access=access_value).values('first_name', 'last_name', 'email', 'date_joined', 'access')
        else:
            return JsonResponse({'error': 'Invalid access type'}, status=400)

    users_list = list(users)  # Convert ValuesQuerySet to a list
    for user in users_list:
        if user['first_name'] is None:
            user['first_name'] = ' '
        if user['last_name'] is None:
            user['last_name'] = ' '
        user['access'] = reverse_access_map.get(user['access'], 'unknown')
            
    return JsonResponse(users_list, safe=False)


@api_view(['GET'])
def visit_data(request):
    email = request.query_params.get('email')

    return JsonResponse({}, safe=False)
    



    


