from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(model_name='product', name='product_id',
            field=models.CharField(blank=True, default='', max_length=20)),
        migrations.AlterField(model_name='product', name='product_id',
            field=models.CharField(blank=True, max_length=20, unique=True)),
        migrations.AddField(model_name='product', name='subcategory',
            field=models.CharField(blank=True, default='', max_length=100)),
        migrations.AddField(model_name='product', name='brand',
            field=models.CharField(blank=True, default='', max_length=100)),
        migrations.AddField(model_name='product', name='gender',
            field=models.CharField(blank=True, default='', max_length=20)),
        migrations.AddField(model_name='product', name='size',
            field=models.CharField(blank=True, default='', max_length=20)),
        migrations.AddField(model_name='product', name='color',
            field=models.CharField(blank=True, default='', max_length=50)),
        migrations.AddField(model_name='product', name='material',
            field=models.CharField(blank=True, default='', max_length=100)),
        migrations.AddField(model_name='product', name='unit_price',
            field=models.FloatField(default=0)),
        migrations.AddField(model_name='product', name='cost_price',
            field=models.FloatField(default=0)),
        migrations.AddField(model_name='product', name='supplier_id',
            field=models.CharField(blank=True, default='', max_length=20)),
        migrations.AddField(model_name='product', name='supplier_name',
            field=models.CharField(blank=True, default='', max_length=100)),
        migrations.AddField(model_name='product', name='lead_time_days',
            field=models.IntegerField(default=7)),
    ]
