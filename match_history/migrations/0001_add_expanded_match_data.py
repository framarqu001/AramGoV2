from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='expanded_match_data',
            field=models.JSONField(blank=True, null=True),
        ),
    ]