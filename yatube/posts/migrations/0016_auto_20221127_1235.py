# Generated by Django 2.2.16 on 2022-11-27 09:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0015_auto_20221127_1233'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='Follow',
        ),
        migrations.AlterUniqueTogether(
            name='follow',
            unique_together=set(),
        ),
    ]
