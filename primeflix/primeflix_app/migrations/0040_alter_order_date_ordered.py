# Generated by Django 3.2.9 on 2021-12-30 23:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('primeflix_app', '0039_auto_20211231_0033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date_ordered',
            field=models.DateTimeField(default=datetime.datetime(2021, 12, 31, 0, 34, 0, 39659)),
        ),
    ]
