# Generated by Django 4.0.3 on 2022-04-05 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_alter_product_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, default='images/placeholder.jpeg', null=True, upload_to='images/', verbose_name='Изображение'),
        ),
    ]
