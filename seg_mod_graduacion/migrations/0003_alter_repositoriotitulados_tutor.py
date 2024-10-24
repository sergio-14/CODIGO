# Generated by Django 5.1 on 2024-10-21 16:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seg_mod_graduacion', '0002_actaexcelencia'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='repositoriotitulados',
            name='tutor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='repo_tutor', to=settings.AUTH_USER_MODEL),
        ),
    ]
