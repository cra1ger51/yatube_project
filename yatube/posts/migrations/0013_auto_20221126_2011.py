# Generated by Django 2.2.16 on 2022-11-26 17:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0012_auto_20221126_1958'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='follow',
            unique_together=set(),
        ),
    ]