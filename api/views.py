from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
from bed.models import BedStat
from treatment.models import Certificate
from api.serializers import BedStatSerializer, CertificateSerializer
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from django.db.models import F
from collections import defaultdict

# Create your views here.
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
    


    



    


