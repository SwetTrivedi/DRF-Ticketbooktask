# Generated by Django 5.0.1 on 2025-05-09 13:07

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketbooking', '0003_alter_train_departuretimedate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='train',
            name='arrivaldatetime',
            field=models.DateTimeField(default=datetime.datetime(2025, 5, 9, 13, 7, 37, 470523)),
        ),
        migrations.AlterField(
            model_name='train',
            name='departuretimedate',
            field=models.DateTimeField(default=datetime.datetime(2025, 5, 9, 13, 7, 37, 470523)),
        ),
    ]
