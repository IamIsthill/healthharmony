from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse
from bed.models import BedStat
from .serializers import BedStatSerializer

# Create your views here.
@api_view(['GET'])
def api_data(request):
    beds = BedStat.objects.all()
    serializer = BedStatSerializer(beds, many=True)
    return Response(serializer.data)
    # return JsonResponse(serializer.data, safe=True)