# Generated by Django 5.0.6 on 2024-06-25 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('electroapp', '0008_rename_pname_order_total_remove_order_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_id',
            field=models.CharField(max_length=255, null=True),
        ),
    ]