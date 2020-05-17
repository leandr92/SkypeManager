# Generated by Django 3.0.5 on 2020-04-19 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CallList', '0008_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='skype_login',
            field=models.CharField(default='', max_length=200, verbose_name='Логин Skype'),
        ),
        migrations.AddField(
            model_name='account',
            name='skype_password',
            field=models.CharField(default='', max_length=200, verbose_name='Пароль Skype'),
        ),
        migrations.AlterField(
            model_name='account',
            name='last_login',
            field=models.DateTimeField(auto_now=True, verbose_name='последний логин'),
        ),
        migrations.DeleteModel(
            name='SkypeAuth',
        ),
    ]
