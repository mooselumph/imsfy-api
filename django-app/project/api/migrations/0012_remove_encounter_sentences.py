# Generated by Django 2.2.3 on 2019-07-17 23:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_auto_20190717_2315'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='encounter',
            name='sentences',
        ),
    ]
