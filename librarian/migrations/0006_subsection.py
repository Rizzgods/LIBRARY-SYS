# Generated by Django 5.0.3 on 2024-08-30 13:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('librarian', '0005_alter_books_borrowed'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Def', max_length=100)),
                ('code', models.CharField(default='', max_length=100)),
                ('sub_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='librarian.subcategory')),
            ],
        ),
    ]
