# Generated by Django 4.2.6 on 2024-12-29 16:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("web", "0002_remove_course_image_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="faculty",
            name="is_staff",
            field=models.BooleanField(
                default=True, help_text="If checked will show up in the Faculty section"
            ),
        ),
        migrations.AlterField(
            model_name="faculty",
            name="image_url",
            field=models.URLField(
                default="https://lairesit.sirv.com/rb_859.png",
                help_text="IMPORTANT: Update this value incase of staff (is staff)",
                null=True,
            ),
        ),
    ]