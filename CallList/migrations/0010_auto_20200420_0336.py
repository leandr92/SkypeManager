# Generated by Django 3.0.5 on 2020-04-19 23:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CallList', '0009_auto_20200420_0101'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contact',
            old_name='contactName',
            new_name='contactId',
        ),
        migrations.RemoveField(
            model_name='contact',
            name='contactView',
        ),
        migrations.RemoveField(
            model_name='contact',
            name='use',
        ),
    ]
