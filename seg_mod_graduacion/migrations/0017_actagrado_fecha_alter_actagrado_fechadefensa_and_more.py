# Generated by Django 5.1 on 2024-10-28 19:14

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seg_mod_graduacion', '0016_actagrado'),
    ]

    operations = [
        migrations.AddField(
            model_name='actagrado',
            name='fecha',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='actagrado',
            name='fechadefensa',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='actagrado',
            name='fechadefensa_1',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='actagrado',
            name='fechadefensa_2',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='actagrado',
            name='fechadefensa_3',
            field=models.DateField(),
        ),
    ]
