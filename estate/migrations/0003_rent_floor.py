# Generated by Django 5.0 on 2023-12-24 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estate', '0002_alter_rent_options_alter_rent_area_alter_rent_city_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='rent',
            name='floor',
            field=models.CharField(default=1, max_length=10, verbose_name='Этаж'),
            preserve_default=False,
        ),
    ]
