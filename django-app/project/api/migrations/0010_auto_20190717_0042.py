# Generated by Django 2.2.3 on 2019-07-17 00:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_auto_20190716_2348'),
    ]

    operations = [
        migrations.AlterField(
            model_name='encounter',
            name='word',
            field=models.CharField(default='', max_length=100),
        ),
    ]
