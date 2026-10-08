from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0004_shop_owner_category'),
        ('products', '0004_alter_product_product_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='shop',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='products',
                to='shops.shop',
            ),
        ),
        migrations.AlterField(
            model_name='product',
            name='product_id',
            field=models.CharField(blank=True, default=None, max_length=20, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='product',
            unique_together={('shop', 'product_id')},
        ),
    ]
