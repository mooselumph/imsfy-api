# Generated by Django 2.2.3 on 2019-07-15 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_form_gloss_sense_word'),
    ]

    operations = [
        migrations.AlterField(
            model_name='form',
            name='information',
            field=models.CharField(default='', max_length=1000),
        ),
        migrations.AlterField(
            model_name='sense',
            name='misc',
            field=models.CharField(default='', max_length=500),
        ),
        migrations.AlterField(
            model_name='sense',
            name='sense_information',
            field=models.CharField(default='', max_length=1000),
        ),
        migrations.AlterField(
            model_name='word',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
