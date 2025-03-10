# Generated by Django 5.0.6 on 2024-10-08 09:25

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="InventoryDetail",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "item_no",
                    models.SmallIntegerField(blank=True, default=None, null=True),
                ),
                ("unit", models.CharField(max_length=50, null=True)),
                ("item_name", models.CharField(max_length=100, null=True)),
                (
                    "category",
                    models.CharField(
                        choices=[("Medicine", "Medicine"), ("Supply", "Supply")],
                        default="Medicine",
                        max_length=10,
                        null=True,
                    ),
                ),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "expiration_date",
                    models.DateField(blank=True, default=None, null=True),
                ),
            ],
        ),
        migrations.CreateModel(
            name="QuantityHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("updated_quantity", models.IntegerField(null=True)),
                ("timestamp", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
