# Generated by Django 4.0.1 on 2022-01-15 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0030_program_venue'),
    ]

    operations = [
        migrations.RenameField(
            model_name='program',
            old_name='registration_open',
            new_name='online_registration_open',
        ),
        migrations.AddField(
            model_name='program',
            name='spot_registration_open',
            field=models.BooleanField(default=True),
        ),
    ]
