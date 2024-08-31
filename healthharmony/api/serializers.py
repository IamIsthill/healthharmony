from rest_framework.serializers import ModelSerializer, SerializerMethodField
from healthharmony.models.bed.models import BedStat
from healthharmony.models.treatment.models import Certificate


class BedStatSerializer(ModelSerializer):
    class Meta:
        model = BedStat
        fields = "__all__"


class CertificateSerializer(ModelSerializer):
    email = SerializerMethodField()
    first_name = SerializerMethodField()
    last_name = SerializerMethodField()

    def get_email(self, obj):
        return obj.patient.email if obj.patient else None

    def get_first_name(self, obj):
        return obj.patient.first_name if obj.patient else None

    def get_last_name(self, obj):
        return obj.patient.last_name if obj.patient else None

    class Meta:
        model = Certificate
        fields = "__all__"
