# Generated by Django 5.0.6 on 2024-07-07 05:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_rename_name_userinfo_username"),
    ]

    operations = [
        migrations.AddField(
            model_name="userinfo",
            name="status",
            field=models.IntegerField(
                choices=[(0, "不活跃"), (1, "活跃")], default=0, verbose_name="状态"
            ),
        ),
        migrations.AlterField(
            model_name="userinfo",
            name="token",
            field=models.CharField(
                blank=True,
                db_index=True,
                max_length=64,
                null=True,
                verbose_name="TOKEN",
            ),
        ),
        migrations.AlterField(
            model_name="userinfo",
            name="username",
            field=models.CharField(db_index=True, max_length=32, verbose_name="用户名"),
        ),
    ]
