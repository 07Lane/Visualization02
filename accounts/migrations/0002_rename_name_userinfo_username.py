# Generated by Django 5.0.6 on 2024-07-06 03:24

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="userinfo",
            old_name="name",
            new_name="username",
        ),
    ]
