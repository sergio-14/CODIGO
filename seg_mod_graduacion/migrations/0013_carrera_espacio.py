# Generated by Django 5.1 on 2024-10-28 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seg_mod_graduacion', '0012_facultad_espacio'),
    ]

    operations = [
        migrations.AddField(
            model_name='carrera',
            name='Espacio',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
