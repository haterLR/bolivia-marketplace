from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [('marketplace', '0001_initial'), ('users', '0001_initial')]

    operations = [
        migrations.CreateModel(
            name='ChatThread',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buyer_threads', to='users.user')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seller_threads', to='users.user')),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='chat_thread', to='marketplace.order')),
            ],
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('attachment', models.ImageField(blank=True, null=True, upload_to='chat/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.user')),
                ('thread', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chatapp.chatthread')),
            ],
        ),
    ]
