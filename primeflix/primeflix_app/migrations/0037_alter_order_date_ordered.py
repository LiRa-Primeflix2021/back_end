# Generated by Django 3.2.9 on 2021-12-30 15:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primeflix_app', '0036_alter_order_date_ordered'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date_ordered',
            field=models.DateTimeField(default=datetime.datetime(2021, 12, 30, 16, 35, 45, 391679)),
        ),
    ]