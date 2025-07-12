from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import OutfitHistoryForm
from .models import OutfitHistory
from fitting_room.models import Look

# Create your views here.
@login_required
def history(request):
    entries = OutfitHistory.objects.filter(user=request.user).order_by('-date')
    return render(request, 'history/history.html', {'entries': entries})

@login_required
def log_outfit(request):
    if request.method == 'POST':
        form = OutfitHistoryForm(request.POST)
        form.fields['look'].queryset = Look.objects.filter(user=request.user) # limit choices to user's looks
        if form.is_valid():
            outfit = form.save(commit=False)
            outfit.user = request.user
            outfit.save()
            return redirect('history:history')
    else:
        form = OutfitHistoryForm()
        form.fields['look'].queryset = Look.objects.filter(user=request.user)

    return render(request, 'history/log_outfit.html', {'form': form})
