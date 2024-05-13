from rest_framework.serializers import ModelSerializer
from bed.models import BedStat

class BedStatSerializer(ModelSerializer):
    class Meta:
        model = BedStat
        fields = '__all__'