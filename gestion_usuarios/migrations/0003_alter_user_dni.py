# Generated by Django 5.1 on 2024-10-26 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestion_usuarios', '0002_user_dni'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='dni',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True, verbose_name='Carnet Identidad:'),
        ),
    ]
