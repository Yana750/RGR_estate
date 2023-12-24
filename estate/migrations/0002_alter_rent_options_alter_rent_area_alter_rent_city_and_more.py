# Generated by Django 5.0 on 2023-12-23 18:40

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estate', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rent',
            options={'ordering': ['-fixed', '-time_create'], 'verbose_name': 'Аренда', 'verbose_name_plural': 'Аренда'},
        ),
        migrations.AlterField(
            model_name='rent',
            name='area',
            field=models.IntegerField(blank=True, null=True, verbose_name='Площаль помещения'),
        ),
        migrations.AlterField(
            model_name='rent',
            name='city',
            field=models.CharField(max_length=100, verbose_name='Город'),
        ),
        migrations.AlterField(
            model_name='rent',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Стоимость аренды'),
        ),
        migrations.AlterField(
            model_name='rent',
            name='status',
            field=models.CharField(choices=[('reserved', 'Забронировано'), ('free', 'Свободно')], default='published', max_length=10, verbose_name='Статус помещения'),
        ),
        migrations.AlterField(
            model_name='rent',
            name='thumbnail',
            field=models.ImageField(blank=True, upload_to='images/thumbnails/%Y/%m/%d/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=('png', 'jpg', 'webp', 'jpeg', 'gif'))], verbose_name='Превью помещения'),
        ),
    ]
