from django.test import TestCase
from bed.models import BedStat

class BedTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # This method is called once at the beginning to set up non-modifiable data for the entire class
        BedStat.objects.create(status=True)
        BedStat.objects.create(status=False)
        BedStat.objects.create()  # This will use the default status (False)

    def test_bed_status_true(self):
        bed = BedStat.objects.get(id=1)
        self.assertTrue(bed.status)

    def test_bed_status_false(self):
        bed = BedStat.objects.get(id=2)
        self.assertFalse(bed.status)

    def test_bed_status_default(self):
        bed = BedStat.objects.get(id=3)
        self.assertFalse(bed.status)

    def test_multiple_beds(self):
        beds = BedStat.objects.all()
        self.assertEqual(beds.count(), 3)

    def test_bed_str_representation_true(self):
        bed = BedStat.objects.get(id=1)
        self.assertEqual(str(bed), 'Bed 1 - Status: Occupied')

    def test_bed_str_representation_false(self):
        bed = BedStat.objects.get(id=2)
        self.assertEqual(str(bed), 'Bed 2 - Status: Available')

    def test_toggle_status(self):
        bed = BedStat.objects.get(id=1)
        bed.status = not bed.status
        bed.save()
        self.assertFalse(BedStat.objects.get(id=1).status)
