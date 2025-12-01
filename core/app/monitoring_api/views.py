from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import datetime # Import to get dynamic 
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth import logout as auth_logout
from django.core import serializers
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Activity
from .serializers import ActivitySerializer
from django.contrib.auth import logout as auth_logout

import json
@csrf_exempt
def index(request):
    data = {
        "status":"",
        "user":""     
    }
    print(request)
    
    if request.user.is_authenticated:
        data['status'] = 'Login Already' 
        data['user'] = { 
            'id': request.user.id,
            'username': request.user.username,
        }
        data['ok'] = 200
        
        return JsonResponse(data)
        
    else:    
        if request.method == 'POST':
            body = json.loads(request.body)
            username = body.get('username', 'N/A')
            password = body.get('password', 'N/A')
            user = authenticate(request,username=username,password=password)
          
            if user is not None:
                if user.is_active:
                    data['status'] = 'Login Successfull' 
                    data['user'] = { 
                        'id': user.id,
                        'username': user.username,
                    }
                    data['ok'] = 200
                else:    
                    data['ok'] = 404
                    data['status'] = 'Not Yet Active' 
                    
            else:
                data['status'] = 'Invalid Credentials'
                data['ok'] = 404
                
                
            
            # Use JsonResponse to serialize the dictionary into JSON 
            # and set the Content-Type header to application/json.
            return JsonResponse(data)
from datetime import date
def get_filter_date(request):
    date_param = request.query_params.get('date')
    if date_param:
        try:
            return date.fromisoformat(date_param)
        except ValueError:
            pass # Fall back to today if date is invalid
    return timezone.now().date()


@csrf_exempt
@api_view(['GET'])
def view_activity(request):
    # 1. Get the date from query parameters or default to today
    filter_date = get_filter_date(request)
    
    # 2. Filter for the specific date AND PENDING status
    activities = Activity.objects.filter(
        date=filter_date,
        status='PENDING' 
    ).order_by('time') 
    print(filter_date)
    serializer = ActivitySerializer(activities, many=True)
    return Response(serializer.data) 

@csrf_exempt
@api_view(['GET'])
def view_activity_done(request):
    # 1. Get the date from query parameters or default to today
    filter_date = get_filter_date(request)
    
    # 2. Filter for the specific date AND completed status (assuming 'YES')
    # If you want to show only 'YES' (Completed) tasks:
    activities = Activity.objects.filter(
        date=filter_date,
        status__in=['YES','NO']
    ).order_by('time')
    
    # If you want to show ALL non-pending tasks ('YES' and 'NO'):
    # activities = Activity.objects.filter(date=filter_date, status__in=['NO','YES']).order_by('time')

    serializer = ActivitySerializer(activities, many=True)
    return Response(serializer.data)
@csrf_exempt
def update_status(request):
    body = json.loads(request.body)
    id = body.get('id', 'N/A')
    status = body.get('status', 'N/A')
    data = {
        "status":"",
        "ok":""     
    }
    try:
        activity = Activity.objects.get(id=id)
        activity.status = status
        activity.save()
        data['status'] = 'Updated Successfully'
        data['ok'] = 200
        return JsonResponse(data)
        
    except Exception: 
        data['status'] = 'Updating Error'
        data['ok'] = 404
        return JsonResponse(data)

@csrf_exempt
def user_logout(request):

    data = {
        "status": "Logout Failed",
        "ok": 404
    }
    print(request)
    if request.user.is_authenticated:
        # Use the imported Django logout function
        auth_logout(request)
        
        data['status'] = 'Logout Successful'
        data['ok'] = 200
        return JsonResponse(data)
    else:
        data['status'] = 'No user is currently logged in'
        data['ok'] = 200 # Often treated as a successful operation (nothing to log out)
        return JsonResponse(data)
    
@csrf_exempt
def add_event(request):
    data = {
        "status": "Adding Event Failed",
        "ok": 400 
    }
    
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            # Keys match the React Native data structure: name, datetime, description, priority
            title = body.get('title') 
            date = body.get('date')
            time = body.get('time')
            note = body.get('note', '')
            priority = body.get('priority')
            status = "PENDING"
            
            # 1. Input Validation
            if not all([title,date,time, priority]):
                data['status'] = 'Missing required fields (name, datetime, priority).'
                return JsonResponse(data, status=400)

           
            # 4. Create the Activity object
            # Mapped to your model fields: title, date, time, msg, types, status
            event = Activity.objects.create(
                title=title,
                date=date,
                time=time,
                msg=note, 
                types=priority,
                status=status
            )
            
            data['status'] = 'Event Added Successfully'
            data['event_id'] = event.id
            data['ok'] = 200
            return JsonResponse(data, status=200)
            
        except json.JSONDecodeError:
            data['status'] = 'Invalid JSON in request body.'
            return JsonResponse(data, status=400)
            
        except ValueError:
            # Catches error if fromisoformat fails due to format issues
            data['status'] = 'Invalid date/time format provided.'
            return JsonResponse(data, status=400)
            
        except Exception as e: 
            # Catch database or any unexpected errors
            data['status'] = f'Internal server error: {e}'
            print(f"Error creating activity: {e}")
            return JsonResponse(data, status=500)
            
    else:
        data['status'] = f'Method {request.method} not allowed.'
        return JsonResponse(data, status=405)