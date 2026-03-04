from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [('users', '0001_initial')]

    operations = [
        migrations.CreateModel(name='Category', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('name', models.CharField(max_length=120, unique=True))]),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('buyer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cart', to='users.user')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_bob', models.DecimalField(decimal_places=2, max_digits=12)),
                ('status', models.CharField(choices=[('creado', 'Creado'), ('pagado', 'Pagado'), ('verificando', 'Verificando'), ('enviado', 'Enviado'), ('entregado', 'Entregado'), ('cancelado', 'Cancelado')], default='creado', max_length=20)),
                ('address', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=120)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='users.user')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales_orders', to='users.user')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('price_bob', models.DecimalField(decimal_places=2, max_digits=12)),
                ('stock', models.PositiveIntegerField()),
                ('city', models.CharField(max_length=120)),
                ('published', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='marketplace.category')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='users.user')),
            ],
        ),
        migrations.CreateModel(name='ProductImage', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('image', models.ImageField(upload_to='products/')), ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='marketplace.product'))]),
        migrations.CreateModel(name='OrderItem', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('quantity', models.PositiveIntegerField()), ('unit_price_bob', models.DecimalField(decimal_places=2, max_digits=12)), ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='marketplace.order')), ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='marketplace.product'))]),
        migrations.CreateModel(name='Payment', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('method', models.CharField(choices=[('TIGO_MONEY', 'Tigo Money'), ('QR_INTEROP', 'QR Interop'), ('TRANSFERENCIA', 'Transferencia')], max_length=20)), ('status', models.CharField(choices=[('creado', 'Creado'), ('verificando', 'Verificando'), ('pagado', 'Pagado'), ('rechazado', 'Rechazado')], default='creado', max_length=20)), ('reference', models.CharField(blank=True, max_length=120)), ('metadata', models.JSONField(blank=True, default=dict)), ('proof_image', models.ImageField(blank=True, null=True, upload_to='payments/')), ('created_at', models.DateTimeField(auto_now_add=True)), ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='marketplace.order'))]),
        migrations.CreateModel(name='CartItem', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('quantity', models.PositiveIntegerField(default=1)), ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='marketplace.cart')), ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='marketplace.product'))], options={'unique_together': {('cart', 'product')}}),
    ]
