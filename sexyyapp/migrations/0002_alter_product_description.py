# Generated by Django 3.2.7 on 2021-09-22 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sexyyapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(),
        ),
    ]
