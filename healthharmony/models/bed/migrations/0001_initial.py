# Generated by Django 5.0.6 on 2024-10-08 09:25

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Ambulansya",
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
                ("is_avail", models.BooleanField(blank=True, default=False, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="BedStat",
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
                ("status", models.BooleanField(blank=True, default=False)),
            ],
        ),
        migrations.CreateModel(
            name="WheelChair",
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
                ("is_avail", models.BooleanField(default=False)),
                ("quantity", models.PositiveIntegerField(default=0)),
                ("updated", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-updated"],
            },
        ),
    ]
