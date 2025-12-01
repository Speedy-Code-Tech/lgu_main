# app/monitoring_api/serializers.py

from rest_framework import serializers
from .models import Activity # Use the correct model name (Activities or Activity)

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity # Use the correct model name here
        fields = '__all__' # Include all fields from the model