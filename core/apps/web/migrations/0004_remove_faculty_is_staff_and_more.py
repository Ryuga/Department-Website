# Generated by Django 4.2.6 on 2024-12-29 16:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0003_faculty_is_staff_alter_faculty_image_url"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="faculty",
            name="is_staff",
        ),
        migrations.AddField(
            model_name="faculty",
            name="is_student_coordinator",
            field=models.BooleanField(
                default=True,
                help_text="If checked will not show up in the Faculty section",
            ),
        ),
        migrations.AlterField(
            model_name="faculty",
            name="image_url",
            field=models.URLField(
                default="https://lairesit.sirv.com/rb_859.png",
                help_text="[!IMPORTANT!]: Update incase of non student coordinators as it will show upin faculty section",
                null=True,
            ),
        ),
    ]