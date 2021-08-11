# Generated by Django 3.2.4 on 2021-08-09 20:28

from django.db import migrations, models
import web.models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0016_alter_gallery_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='IpHash',
            fields=[
                ('hash', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('creation_time', models.DateTimeField(default=web.models.time_now)),
            ],
        ),
    ]