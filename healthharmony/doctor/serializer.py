from rest_framework import serializers
from healthharmony.models.treatment.models import (
    Illness,
    IllnessTreatment,
    Category,
    IllnessNote,
)
from healthharmony.models.inventory.models import InventoryDetail
from healthharmony.users.models import User, Department


class IllnessSerializer(serializers.ModelSerializer):
    patient_email = serializers.CharField(source="patient.email", read_only=True)
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
    doctor_email = serializers.CharField(source="doctor.email", read_only=True)
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


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryDetail
        fields = ["item_name"]


class UserSerializer(serializers.ModelSerializer):

    department_name = serializers.CharField(
        source="department.department", read_only=True
    )

    class Meta:
        model = User
        exclude = [
            "password",
            "user_permissions",
            "is_active",
            "is_staff",
            "is_superuser",
            "last_login",
            "groups",
            "access",
        ]


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Department


class IllnessNoteSerializer(serializers.ModelSerializer):
    doctor_first_name = serializers.CharField(
        source="noted_by.first_name", read_only=True
    )
    doctor_last_name = serializers.CharField(
        source="noted_by.last_name", read_only=True
    )
    doctor_email = serializers.CharField(source="noted_by.email", read_only=True)

    class Meta:
        fields = "__all__"
        model = IllnessNote
