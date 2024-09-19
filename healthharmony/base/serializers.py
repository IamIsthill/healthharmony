from rest_framework import serializers
from healthharmony.models.treatment.models import DoctorDetail
from healthharmony.users.models import User


class DoctorSerializer(serializers.ModelSerializer):
    time_avail_start = serializers.TimeField(
        source="doctordetail_set.first.time_avail_start", read_only=True
    )
    time_avail_end = serializers.TimeField(
        source="doctordetail_set.first.time_avail_end", read_only=True
    )
    avail = serializers.BooleanField(
        source="doctordetail_set.first.avail", read_only=True
    )

    class Meta:
        fields = "__all__"
        model = User
