# Generated by Django 2.2.3 on 2019-07-17 23:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_remove_encounter_sentences'),
    ]

    operations = [
        migrations.AddField(
            model_name='encounter',
            name='sentences',
            field=models.ManyToManyField(to='api.Sentence'),
        ),
    ]
