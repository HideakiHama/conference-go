# Generated by Django 4.0.3 on 2022-09-29 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='conference',
            name='city',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='conference',
            name='state',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='picture_url',
            field=models.URLField(null=True),
        ),
    ]
