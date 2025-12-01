from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# MODELS
from .models import Events,Venues
# Create your views here.
@login_required
def view(request):
    context = {
        'events':Events.objects.select_related('venue').all().order_by('-from_date'),
        "active":'event'
    }
    return render(request,'view.html',context)

@login_required
def create(request):
    if request.method == 'POST':
        # Get form data
        event_name   = request.POST.get('event_name', '').strip()
        venue_id     = request.POST.get('venue')
        from_date    = request.POST.get('from_date')
        to_date      = request.POST.get('to_date')
        coordinator  = request.POST.get('coordinator', '').strip()
        status       = request.POST.get('status')
        remarks      = request.POST.get('remarks', '').strip()

        has_error = False

        # === VALIDATION ===
        if not event_name:
            messages.error(request, "Event Name is required.")
            has_error = True
        if not from_date:
            messages.error(request, "From date is required.")
            has_error = True
        if not to_date:
            messages.error(request, "To date is required.")
            has_error = True
        if not coordinator:
            messages.error(request, "Event Coordinator is required.")
            has_error = True
        if not venue_id:
            messages.error(request, "Venue is required.")
            has_error = True
        if not status or status not in {'ongoing', 'pending', 'done', 'cancelled'}:
            messages.error(request, "Please select a valid status.")
            has_error = True

        # Date logic
        if from_date and to_date:
            try:
                from_dt = timezone.datetime.fromisoformat(from_date.replace('T', ' '))
                to_dt   = timezone.datetime.fromisoformat(to_date.replace('T', ' '))
                if from_dt >= to_dt:
                    messages.error(request, "'From' date must be earlier than 'To' date.")
                    has_error = True
            except ValueError:
                messages.error(request, "Invalid date format.")
                has_error = True

        # === IF ERRORS → RE-RENDER WITH DATA ===
        if has_error:
            return render(request, 'create.html', {
                'venues': Venues.objects.all(),
                'event_name': event_name,
                'from_date': from_date,
                'to_date': to_date,
                'coordinator': coordinator,
                'status': status,
                'remarks': remarks,
                'selected_venue': venue_id,
                "active":'event'
            })

        # === SAVE ===
        Events.objects.create(
            event_name=event_name,
            from_date=from_date,
            to_date=to_date,
            coordinator=coordinator,
            status=status,
            remarks=remarks,
            venue_id=venue_id
        )
        messages.success(request, "Event created successfully!")
        return redirect('event')

    # === GET → empty form ===
    return render(request, 'create.html', {
        'venues': Venues.objects.all(),
        "active":'event'
    })

@login_required           
def destroy(request):
    try:
        if request.method == 'POST':
            id = request.POST.get('id')
            Events.objects.filter(id=id).first().delete()
            messages.success(request, "Event Deleted successfully!")
            return redirect('event')
            
    except Exception as e:
            messages.success(request, "Event Deleting Failed!")
            return redirect('event')


@login_required
def edit(request,id):
    if request.method == 'POST':
        
        ids = request.POST.get('ids')
        venue = request.POST.get('venue')
        event = get_object_or_404(Events, id=id)
        event_name = request.POST.get('event_name')
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        coordinator = request.POST.get('coordinator')
        status = request.POST.get('status')
        remarks = request.POST.get('remarks')
        has_error = False

        # ---- Event Name -------------------------------------------------
        if not event_name:
            messages.error(request, "Event Name is required.")
            has_error = True

        # ---- Dates -------------------------------------------------------
        if not from_date:
            messages.error(request, "From date is required.")
            has_error = True
        if not to_date:
            messages.error(request, "To date is required.")
            has_error = True

        # make sure dates are valid and from <= to
        if from_date and to_date:
            try:
                from_dt = timezone.datetime.fromisoformat(from_date.replace('T', ' '))
                to_dt   = timezone.datetime.fromisoformat(to_date.replace('T', ' '))
                if from_dt >= to_dt:
                    messages.error(request, "'From' date must be earlier than 'To' date.")
                    has_error = True
            except ValueError:
                messages.error(request, "Invalid date format.")
                has_error = True

        # ---- Coordinator -------------------------------------------------
        if not coordinator:
            messages.error(request, "Event Coordinator is required.")
            has_error = True

        if not venue:
            messages.error(request, "Venue is required.")
            has_error = True

        # ---- Status ------------------------------------------------------
        valid_statuses = {'ongoing', 'pending', 'done', 'cancelled'}
        if not status or status not in valid_statuses:
            messages.error(request, "Please select a valid status.")
            has_error = True

        # ------------------------------------------------------------------
        # 3. If any error → re-render the form with the posted values
        # ------------------------------------------------------------------
        if has_error:
            # keep the entered data so the user does not lose it
            context = {
                'event_name':   event_name,
                'from_date':    from_date,
                'to_date':      to_date,
                'coordinator':  coordinator,
                'status':       status,
                'remarks':      remarks,
                'venue':        venue,
                "active":'event'
            }
            return render(request, 'edit.html', context)
        
        event.event_name = event_name
        event.venue_id = venue
        event.from_date = from_date
        event.to_date = to_date
        event.coordinator = coordinator
        event.status = status
        event.remarks = remarks
        event.save()
        messages.success(request, f"Event '{event_name}' updated successfully!")
        return redirect('event')
    else:
        
        try:
            event = Events.objects.filter(id=id).first()
            context = {
                'event':event,
                'venues':Venues.objects.all()
            }
            return render(request,'edit.html',context)
        except Exception as e:
            messages.error(request,"Something Went Wrong")
            return redirect('event')

@login_required        
def show(request,id):
    context = {
        'event':Events.objects.select_related('venue').filter(id=id).first,
    }
    return render(request,'show.html',context)

from django.http import JsonResponse
from django.db.models import Q
def calendar(request):
    return render(request, 'calendar.html')

def event_api(request):
    events = Events.objects.select_related('venue').filter(~Q(status__in=['Done','Cancelled'])).all()
    event_list = []

    for e in events:
        event_list.append({
            'title': e.event_name,
            'start': e.from_date.isoformat(),
            'end': e.to_date.isoformat(),
            'extendedProps': {
                'venue': e.venue.venue if e.venue else 'No venue',
                'coordinator': e.coordinator,
                'status': e.status,
                'remarks': e.remarks or ''
            },
            'backgroundColor': {
                'ongoing': '#f59e0b',
                'pending': '#3b82f6',
                'done': '#10b981',
                'cancelled': '#ef4444'
            }.get(e.status, '#6b7280'),
        })

    return JsonResponse(event_list, safe=False)