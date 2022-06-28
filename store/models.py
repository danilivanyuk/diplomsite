from distutils.command.upload import upload
from email.policy import default
from django.db import models
from io import BytesIO
from PIL import Image
from django.core.files import File
from django.contrib.auth.models import User
import datetime
from datetime import timedelta
from django.utils import timezone
# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    def customers_count(self):
        total = len(self.user)
        return total

class Category(models.Model):
    name = models.CharField(
        max_length=100, verbose_name="Название категории", db_index=True)
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Создано: ")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Обновлено: ")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


def compress(image):
    im = Image.open(image)
    # create a BytesIO object
    im_io = BytesIO()
    # save image to BytesIO object
    im.save(im_io, 'JPEG', optimize=True, quality=70)
    # create a django-friendly Files object
    new_image = File(im_io, name=image.name)
    return new_image

COLORS = (
    ('черный','черный'),
    ('белый','белый'),
    )
class Product(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, verbose_name='Категория')

    image = models.ImageField(upload_to="images/",blank=True, null=True,
                              verbose_name="Изображение", default="placeholder.jpeg")
    
    title = models.CharField(max_length=60, blank=False, null=False, verbose_name='Название', unique=True)
    stockQuantity = models.IntegerField(default=1, null=False, blank=False, verbose_name='Количество на складе')
    serialNumber = models.IntegerField(default=0, null=False, blank=False, verbose_name='Серийный номер')
    color = models.CharField(choices=COLORS, blank=True, null=True, verbose_name='Цвет', max_length=50)
    cycles = models.IntegerField(default=0, null=True, blank=True, verbose_name='Циклы')
    priceBuy = models.IntegerField(default=0, null=True, blank=True, verbose_name='Цена покупки')
    priceSell = models.IntegerField(default=0, null=True, blank=True, verbose_name='Цена продажи')

    
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Создано: ")
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Обновлено: ")

    def __str__(self):
        return self.title

    # SAVE METHOD

    def save(self, *args, **kwargs):
        # call the compress function
        new_image = compress(self.image)
        # set self.image to new_image
        self.image = new_image
        # save
        super().save(*args, **kwargs)

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
        

    class Meta:
        ordering = ['-title']
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.title


class Order(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, blank=True, null=True)
    ordered_date = models.DateField(
        auto_now_add=True, verbose_name="Дата заказа")
    complete = models.BooleanField(default=False, verbose_name='Заказан')
    finished = models.BooleanField(default=False, verbose_name='Завершен')

    transaction_id = models.CharField(max_length=200, null=True)

    @property
    def get_address(self):
        address = self.shippingadress_set.all()
        return address

    def get_nonfinished_orders(self):
        a = []
        if self.finished != True:
            a.append(self)
        return a

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['-ordered_date']
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def get_finished_orders(self):
        orderproducts = self.orderproduct_set.all()
        return orderproducts

    def get_proceeds(self):
        total = self.get_finished_orders
        return total

    @ property
    def get_cart_total(self):
        orderproducts = self.orderproduct_set.all()
        total = sum([product.get_total for product in orderproducts])
        return total

    @ property
    def get_cart_items(self):
        orderproducts = self.orderproduct_set.all()
        total = sum([product.quantity for product in orderproducts])
        return total

    # def if_less_then_24(self):
    #     return self.ordered_date + timedelta(hours=24) < timezone.now()



class OrderProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.order)

    @ property
    def get_total(self):
        total = self.product.priceSell * self.quantity
        return total

    def reduceQuantity(self):
        self.product.stockQuantity =-1

    class Meta:
        ordering = ['-product']
        verbose_name = "Заказанный товар"
        verbose_name_plural = "Заказанные товары"


class ShippingAdress(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    city = models.CharField(max_length=200, null=False)
    street = models.CharField(max_length=200, null=False)
    house = models.CharField(max_length=200, null=False)
    appartament = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (self.city + ', ' + self.street + ' ' + self.house + ', ' + self.appartament)

    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адреса'
