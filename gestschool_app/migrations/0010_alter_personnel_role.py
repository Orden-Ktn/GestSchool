# Generated by Django 5.1.2 on 2025-03-15 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gestschool_app', '0009_personnel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personnel',
            name='role',
            field=models.CharField(default='Personnel', max_length=100),
        ),
    ]
