from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('shops', '0003_alter_shop_shop_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='owner',
            field=models.OneToOneField(
                blank=True, null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='shop',
                to='auth.user',
            ),
        ),
        migrations.AddField(
            model_name='shop',
            name='category',
            field=models.CharField(blank=True, default='Footwear', max_length=100),
        ),
    ]
