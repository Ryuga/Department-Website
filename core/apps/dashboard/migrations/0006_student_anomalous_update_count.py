# Generated by Django 4.2.6 on 2023-12-02 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_student_last_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='anomalous_update_count',
            field=models.IntegerField(default=0),
        ),
    ]