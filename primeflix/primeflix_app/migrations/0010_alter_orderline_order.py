# Generated by Django 3.2.9 on 2021-11-30 12:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('primeflix_app', '0009_alter_order_customer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderline',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_lines', to='primeflix_app.order'),
        ),
    ]
