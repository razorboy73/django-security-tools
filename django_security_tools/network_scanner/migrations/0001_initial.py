# Generated by Django 5.1.4 on 2024-12-22 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ScanLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_range', models.CharField(max_length=255)),
                ('scanned_at', models.DateTimeField(auto_now_add=True)),
                ('results', models.TextField()),
            ],
        ),
    ]
