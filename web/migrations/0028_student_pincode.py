# Generated by Django 4.0 on 2021-12-21 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0027_student_address_student_city_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='pincode',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]