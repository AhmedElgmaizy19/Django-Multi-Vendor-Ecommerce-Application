# Generated by Django 5.2.1 on 2025-05-26 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauth', '0007_user_otp'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='reset_token',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
