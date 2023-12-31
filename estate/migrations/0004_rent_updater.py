# Generated by Django 5.0 on 2023-12-24 12:45

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estate', '0003_rent_floor'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='rent',
            name='updater',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updater_posts', to=settings.AUTH_USER_MODEL, verbose_name='Обновил'),
        ),
    ]
