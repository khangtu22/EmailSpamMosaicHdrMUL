# Generated by Django 3.1.2 on 2020-11-22 04:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inference', '0004_delete_subfilemodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filemodel',
            name='path',
            field=models.FilePathField(default='/Users/khangtu/PycharmProjects/spam/media/image', path='/Users/khangtu/PycharmProjects/spam/media/image'),
        ),
    ]
