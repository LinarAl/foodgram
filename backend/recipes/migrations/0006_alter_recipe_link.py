# Generated by Django 4.2.20 on 2025-05-16 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_alter_recipe_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='link',
            field=models.CharField(blank=True, max_length=8, unique=True, verbose_name='Короткая ссылка'),
        ),
    ]
