# Generated by Django 4.0 on 2021-12-26 19:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0012_transaction_events_selected_tuple'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='events_selected_tuple',
            new_name='events_selected_json',
        ),
    ]
