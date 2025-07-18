from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('match_history', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='damage_dealt',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='damage_taken',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='vision_score',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='objectives_stolen',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='participant',
            name='objectives_killed',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='ItemPurchase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.IntegerField()),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchases', to='match_history.item')),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_purchases', to='match_history.participant')),
            ],
            options={
                'ordering': ['timestamp'],
            },
        ),
    ]