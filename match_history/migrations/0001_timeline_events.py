from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('match_history', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='has_timeline',
            field=models.BooleanField(default=False, help_text='Indicates if timeline data has been processed for this match'),
        ),
        migrations.AlterField(
            model_name='match',
            name='get_duration',
            field=models.CharField(max_length=10, default='0:00'),
        ),
        migrations.CreateModel(
            name='TimelineEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(choices=[('KILL', 'Kill'), ('ASSIST', 'Assist'), ('DEATH', 'Death'), ('OBJECTIVE', 'Objective'), ('BUILDING', 'Building'), ('ITEM_PURCHASED', 'Item Purchased'), ('LEVEL_UP', 'Level Up'), ('OTHER', 'Other')], max_length=20)),
                ('timestamp', models.IntegerField(help_text='Time in seconds from the start of the match')),
                ('description', models.CharField(max_length=255)),
                ('position_x', models.FloatField(blank=True, help_text='X coordinate on the map', null=True)),
                ('position_y', models.FloatField(blank=True, help_text='Y coordinate on the map', null=True)),
                ('additional_data', models.JSONField(blank=True, help_text='Additional event-specific data', null=True)),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timeline_events', to='match_history.match')),
                ('participants_involved', models.ManyToManyField(related_name='timeline_events', to='match_history.participant')),
            ],
            options={
                'ordering': ['timestamp'],
            },
        ),
    ]