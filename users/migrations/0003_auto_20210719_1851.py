# Generated by Django 3.0.8 on 2021-07-19 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20210719_1843'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(default='media/default.jpg', upload_to='profile_pics'),
        ),
    ]
