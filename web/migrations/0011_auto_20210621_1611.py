# Generated by Django 3.2.4 on 2021-06-21 16:11

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0010_alter_alumni_batch'),
    ]

    operations = [
        migrations.RenameField(
            model_name='course',
            old_name='first_year_syllabus',
            new_name='fifth_sem_syllabus',
        ),
        migrations.RenameField(
            model_name='course',
            old_name='second_year_syllabus',
            new_name='first_sem_syllabus',
        ),
        migrations.RenameField(
            model_name='course',
            old_name='third_year_syllabus',
            new_name='fourth_sem_syllabus',
        ),
        migrations.AddField(
            model_name='course',
            name='second_sem_syllabus',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), blank=True, help_text='Add multiple module names separated by comma', null=True, size=None),
        ),
        migrations.AddField(
            model_name='course',
            name='sixth_sem_syllabus',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), blank=True, help_text='Add multiple module names separated by comma', null=True, size=None),
        ),
        migrations.AddField(
            model_name='course',
            name='third_sem_syllabus',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=50), blank=True, help_text='Add multiple module names separated by comma', null=True, size=None),
        ),
    ]