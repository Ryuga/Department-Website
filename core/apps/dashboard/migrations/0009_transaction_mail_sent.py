# Generated by Django 4.0 on 2021-12-26 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0008_alter_transaction_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='mail_sent',
            field=models.BooleanField(default=False),
        ),
    ]
