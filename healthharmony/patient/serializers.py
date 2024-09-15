from rest_framework import serializers
from healthharmony.models.treatment.models import Certificate


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = "__all__"
