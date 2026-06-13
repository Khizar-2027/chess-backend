from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moves', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='move',
            name='created_at',
        ),
        migrations.AddField(
            model_name='move',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]