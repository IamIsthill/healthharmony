from rest_framework import serializers
from healthharmony.models.treatment.models import Illness, IllnessTreatment, Category


class IllnessSerializer(serializers.ModelSerializer):
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
        fields = "__all__"


class IllnessTreatmentSerializer(serializers.ModelSerializer):
    illness_id = serializers.IntegerField(source="illness.id", read_only=True)
    inventory_detail_name = serializers.CharField(
        source="inventory_detail.item_name", read_only=True
    )
    inventory_detail_category = serializers.CharField(
        source="inventory_detail.category", read_only=True
    )
    inventory_detail_description = serializers.CharField(
        source="inventory_detail.description", read_only=True
    )
    inventory_detail_unit = serializers.CharField(
        source="inventory_detail.unit", read_only=True
    )

    class Meta:
        model = IllnessTreatment
        fields = "__all__"


class IllnessCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "category"]
