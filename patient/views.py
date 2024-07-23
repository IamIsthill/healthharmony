from django.shortcuts import render

# Create your views here.
def overview_view(request):
    context = {}
    return render(request, 'patient/overview.html', context)
