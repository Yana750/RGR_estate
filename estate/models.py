from django.db import models
from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model
from mptt.models import MPTTModel, TreeForeignKey
from django.urls import reverse

from estate.services.utils import unique_slugify

# Create your models here.

#возвращает текущую модель пользователя проекта, что позволяет изменить модель пользователя, используемую в проекте,
#без необходимости изменения кода.
User = get_user_model()
    
class Rent(models.Model):
    """
    Модель постов для сайта
    """

    class RentManager(models.Manager):
        """
        Кастомный менеджер для модели статей
        """
        def all(self):
            """
            Список статей (SQL запрос с фильтрацией для страницы списка статей)
            """
            return self.get_queryset().select_related('author', 'category').filter(status='free')

    STATUS_OPTIONS = (
        ('reserved', 'Забронировано'),
        ('free', 'Свободно')
    )

    ROOM_OPTIONS = (
        ('1-room apartment', '1-комн.'),
        ('2-room apartment', '2-комн.'),
        ('3-room apartment', '3-комн.'),
        ('studio', 'Студия'),
    )
    #например, сдам комнату, сдам студию
    title = models.CharField(verbose_name='Заголовок', max_length=255)
    #ссылка на материал (латиница), или в простонародии ЧПУ,с максимальным количеством символов 255, blank
    slug = models.SlugField(verbose_name='URL', max_length=255, blank=True, unique=True)
    #Город
    city = models.CharField(verbose_name='Город', max_length=100)
    #улица и дом 
    location = models.CharField(verbose_name="Местоположение помещения", max_length=100)
    #этаж
    floor = models.CharField(verbose_name='Этаж', max_length=10)
    #полное описание помещения
    full_description = models.TextField(verbose_name='Полное описание')
    #количество комнат
    room = models.CharField(choices=ROOM_OPTIONS, default='room', verbose_name='Количество комнат', max_length=20)
    #Общая площадь помещения
    area = models.IntegerField(verbose_name='Площаль помещения', blank=True, null=True)
    #стоимость аренды
    price = models.DecimalField(verbose_name='Стоимость аренды', max_digits=10, decimal_places=2)
    #доступность помещения
    status = models.CharField(choices=STATUS_OPTIONS, default='published', verbose_name='Статус помещения', max_length=10)
    #изображение
    thumbnail = models.ImageField(
        verbose_name='Превью помещения', 
        blank=True, 
        upload_to='images/thumbnails/%Y/%m/%d/', 
        validators=[FileExtensionValidator(allowed_extensions=('png', 'jpg', 'webp', 'jpeg', 'gif'))]
    )
    #дата добавления объявления
    time_create = models.DateTimeField(verbose_name="Время добавления", auto_now_add=True)
    # время обновления объявления
    time_update = models.DateTimeField(auto_now=True, verbose_name='Время обновления')
    #Категории
    category = TreeForeignKey('Category', on_delete=models.PROTECT, related_name='rent', verbose_name='Категория')
    #автор объявления
    author = models.ForeignKey(to=User, verbose_name='Автор', on_delete=models.SET_DEFAULT, related_name='author_posts', default=1)
    updater = models.ForeignKey(to=User, verbose_name='Обновил', on_delete=models.SET_NULL, null=True, related_name='updater_posts', blank=True)
    #
    fixed = models.BooleanField(verbose_name='Зафиксировано', default=False)
    

    class Meta:
        db_table = 'app_rent'
        ordering = ['-fixed', '-time_create']
        indexes = [models.Index(fields=['-fixed', '-time_create', 'status'])]
        verbose_name = 'Аренда'
        verbose_name_plural = 'Аренда'

    objects = RentManager()
    
    def __str__(self):
        return self.title + ", " + self.room + " " + str(self.price) + " рублей/месяц"
    
    def get_absolute_url(self):
        return reverse('rent_detail', kwargs={'slug': self.slug})  
    
    def save(self, *args, **kwargs):
        """
        Сохранение полей модели при их отсутствии заполнения
        """
        if not self.slug:
            self.slug = unique_slugify(self, self.title)
        super().save(*args, **kwargs)


#добавить категории
#недвижимость - квартира, комната.
class Category(MPTTModel):
    """
    Модель категорий с вложенностью
    """
    title = models.CharField(max_length=255, verbose_name='Название категории')
    slug = models.SlugField(max_length=255, verbose_name='URL категории', blank=True)
    description = models.TextField(verbose_name='Описание категории', max_length=300)
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_index=True,
        related_name='children',
        verbose_name='Родительская категория'
    )

    class MPTTMeta:
        """
        Сортировка по вложенности
        """
        order_insertion_by = ('title',)

    class Meta:
        """
        Сортировка, название модели в админ панели, таблица в данными
        """
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        db_table = 'app_categories'

    def __str__(self):
        """
        Возвращение заголовка статьи
        """
        return self.title
    def get_absolute_url(self):
        return reverse('rents_by_category', kwargs={'slug': self.slug})