# Generated by Django 2.1.1 on 2018-09-24 10:10

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('apka', '0004_auto_20180921_0800'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='approved',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='task',
            name='date',
            field=models.DateField(default=datetime.datetime(2018, 9, 24, 10, 10, 26, 245266, tzinfo=utc)),
        ),
    ]
