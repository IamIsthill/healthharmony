# Generated by Django 5.0.6 on 2024-10-08 09:25

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BloodPressure",
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
                ("blood_pressure", models.SmallIntegerField(null=True)),
                ("added", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["-added"],
            },
        ),
    ]
