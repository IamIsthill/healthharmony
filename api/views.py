from django.shortcuts import render
from django.http import JsonResponse
from bed.models import BedStat
from .serializers import BedStatSerializer

# Create your views here.
def api_data(request):
    beds = BedStat.objects.all()
    serializer = BedStatSerializer(beds, many=True)
    return JsonResponse(serializer.data, safe=False)