from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match_history', '0001_initial'),  # Replace with the actual latest migration
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='timeline_data',
            field=models.JSONField(blank=True, null=True),
        ),
    ]