# Generated by Django 5.1.2 on 2025-03-16 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestschool_app', '0025_alter_professeur_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='professeur',
            name='contact',
            field=models.CharField(max_length=100),
        ),
    ]
