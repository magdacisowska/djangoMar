# Generated by Django 2.1.1 on 2018-09-20 06:22

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('apka', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='date',
            field=models.DateField(default=datetime.datetime(2018, 9, 20, 6, 22, 42, 577378, tzinfo=utc)),
        ),
    ]
