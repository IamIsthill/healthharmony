from rest_framework import serializers
from healthharmony.models.treatment.models import Illness, IllnessTreatment
from healthharmony.models.inventory.models import InventoryDetail


# Serializer for InventoryDetail
class InventoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryDetail
        fields = [
            "item_no",
            "item_name",
            "unit",
            "category",
            "description",
            "expiration_date",
        ]


# Serializer for IllnessTreatment
class IllnessTreatmentSerializer(serializers.ModelSerializer):
    inventory_detail = InventoryDetailSerializer(read_only=True)

    class Meta:
        model = IllnessTreatment
        fields = ["inventory_detail", "quantity"]


# Serializer for Illness
class IllnessSerializer(serializers.ModelSerializer):
    illness_treatment = serializers.SerializerMethodField()
    patient_first_name = serializers.CharField(
        source="patient.first_name", read_only=True
    )
    patient_last_name = serializers.CharField(
        source="patient.last_name", read_only=True
    )
    staff_first_name = serializers.CharField(source="staff.first_name", read_only=True)
    staff_last_name = serializers.CharField(source="staff.last_name", read_only=True)
    doctor_first_name = serializers.CharField(
        source="doctor.first_name", read_only=True
    )
    doctor_last_name = serializers.CharField(source="doctor.last_name", read_only=True)
    category_name = serializers.CharField(
        source="illness_category.category", read_only=True
    )

    class Meta:
        model = Illness
        fields = [
            "illness_treatment",
            "patient_first_name",
            "patient_last_name",
            "staff_first_name",
            "staff_last_name",
            "doctor_first_name",
            "doctor_last_name",
            "category_name",
            "issue",
            "diagnosis",
            "id",
            "added",
            "updated",
            "treatment",
            "patient",
        ]

    def get_illness_treatment(self, obj):
        treatments = IllnessTreatment.objects.filter(illness=obj)
        return IllnessTreatmentSerializer(treatments, many=True).data
