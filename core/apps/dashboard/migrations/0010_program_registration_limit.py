# Generated by Django 4.2.6 on 2023-12-14 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0009_sitesetting_support_enabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='registration_limit',
            field=models.IntegerField(default=-1),
        ),
    ]
