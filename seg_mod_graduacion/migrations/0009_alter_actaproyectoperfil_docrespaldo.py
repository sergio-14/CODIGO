# Generated by Django 5.1 on 2024-10-26 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seg_mod_graduacion', '0008_actaexcelencia_docrespaldo_actaprivada_docrespaldo_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actaproyectoperfil',
            name='docrespaldo',
            field=models.FileField(blank=True, null=True, upload_to='documento/perfil', verbose_name='Agregar Documentación'),
        ),
    ]