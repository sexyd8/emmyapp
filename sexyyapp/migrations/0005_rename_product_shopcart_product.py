# Generated by Django 3.2.7 on 2021-10-08 09:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sexyyapp', '0004_shopcart_slide'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shopcart',
            old_name='Product',
            new_name='product',
        ),
    ]
