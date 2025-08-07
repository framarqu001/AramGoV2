# Generated manually for expanded match details functionality

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match_history', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='blue_team_towers',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='match',
            name='red_team_towers',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='match',
            name='blue_team_dragons',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='match',
            name='red_team_dragons',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='participant',
            name='damage_dealt',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='participant',
            name='damage_taken',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='participant',
            name='gold_earned',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]