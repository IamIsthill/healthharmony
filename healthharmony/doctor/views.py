from django.shortcuts import render
from treatment.models import Illness

# Create your views here.
def overview_view(request):
    done_illness = Illness.objects.filter(diagnosis__isnull = False)
    not_illness = Illness.objects.filter(diagnosis__isnull = True)

    context = {'done_illness':done_illness, 'not_illness':not_illness}
    return render(request, 'doctor/overview.html', context)
