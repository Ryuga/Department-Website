# Generated by Django 4.0 on 2021-12-21 09:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0030_subevents_reg_fee'),
    ]

    operations = [
        migrations.RenameField(
            model_name='student',
            old_name='college_location',
            new_name='department',
        ),
        migrations.RemoveField(
            model_name='student',
            name='address',
        ),
        migrations.RemoveField(
            model_name='student',
            name='city',
        ),
        migrations.RemoveField(
            model_name='student',
            name='dob',
        ),
        migrations.RemoveField(
            model_name='student',
            name='pincode',
        ),
        migrations.RemoveField(
            model_name='student',
            name='state',
        ),
    ]
