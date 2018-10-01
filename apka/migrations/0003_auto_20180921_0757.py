# Generated by Django 2.1.1 on 2018-09-21 05:57

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('apka', '0002_auto_20180920_0822'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='advancement',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='project',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='task',
            name='date',
            field=models.DateField(default=datetime.datetime(2018, 9, 21, 5, 57, 34, 601183, tzinfo=utc)),
        ),
    ]
