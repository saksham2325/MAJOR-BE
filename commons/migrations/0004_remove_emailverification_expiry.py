# Generated by Django 2.2 on 2022-01-08 15:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('commons', '0003_auto_20211222_1038'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emailverification',
            name='expiry',
        ),
    ]