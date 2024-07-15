from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
from bed.models import BedStat
from treatment.models import Certificate
from api.serializers import BedStatSerializer, CertificateSerializer
from django.utils import timezone
from datetime import timedelta
from django.db.models import F

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

    


