# Generated by Django 4.0 on 2021-12-27 13:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0014_alter_transaction_events_selected_json'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='program',
            name='ending_time',
        ),
        migrations.RemoveField(
            model_name='program',
            name='starting_time',
        ),
    ]