# Generated migration for adding extended participant statistics
# This migration adds KDA ratio and damage statistics fields to the Participant model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        # This migration can be applied to any existing state of the match_history app
        # If there's an initial migration, it will depend on it
        # If not, this will be treated as the first migration for these fields
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='kda_ratio',
            field=models.DecimalField(
                blank=True, 
                decimal_places=2, 
                help_text='KDA ratio calculated as (kills + assists) / max(deaths, 1)', 
                max_digits=6, 
                null=True
            ),
        ),
        migrations.AddField(
            model_name='participant',
            name='total_damage_dealt',
            field=models.BigIntegerField(
                blank=True, 
                help_text='Total damage dealt to all targets', 
                null=True
            ),
        ),
        migrations.AddField(
            model_name='participant',
            name='damage_to_champions',
            field=models.BigIntegerField(
                blank=True, 
                help_text='Total damage dealt to enemy champions', 
                null=True
            ),
        ),
        migrations.AddField(
            model_name='participant',
            name='damage_taken',
            field=models.BigIntegerField(
                blank=True, 
                help_text='Total damage taken from all sources', 
                null=True
            ),
        ),
    ]