# Generated by Django 3.2.9 on 2022-01-01 15:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primeflix_app', '0044_auto_20220101_1658'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shippingaddress',
            name='order',
        ),
        migrations.AlterField(
            model_name='order',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 1, 16, 59, 24, 198766)),
        ),
    ]