# Generated by Django 5.0 on 2023-12-29 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labor', '0002_labor_register_credential_is_sent'),
    ]

    operations = [
        migrations.AddField(
            model_name='labor_register',
            name='otp',
            field=models.CharField(default='569864', max_length=50),
        ),
    ]
