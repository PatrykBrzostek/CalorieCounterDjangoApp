# Generated by Django 3.2.6 on 2021-08-18 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CalorieCounter', '0003_auto_20210818_1322'),
    ]

    operations = [
        migrations.AddField(
            model_name='meal',
            name='fat',
            field=models.FloatField(blank=True, default=0),
        ),
    ]
