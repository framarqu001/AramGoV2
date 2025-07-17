from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match_history', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='role',
            field=models.CharField(choices=[('TOP', 'Top'), ('JUNGLE', 'Jungle'), ('MID', 'Mid'), ('BOTTOM', 'Bottom'), ('SUPPORT', 'Support'), ('FILL', 'Fill'), ('UNSELECTED', 'Unselected')], default='UNSELECTED', max_length=20),
        ),
        migrations.AddField(
            model_name='participant',
            name='rank',
            field=models.CharField(choices=[('IRON', 'Iron'), ('BRONZE', 'Bronze'), ('SILVER', 'Silver'), ('GOLD', 'Gold'), ('PLATINUM', 'Platinum'), ('DIAMOND', 'Diamond'), ('MASTER', 'Master'), ('GRANDMASTER', 'Grandmaster'), ('CHALLENGER', 'Challenger'), ('UNRANKED', 'Unranked')], default='UNRANKED', max_length=20),
        ),
        migrations.AddField(
            model_name='participant',
            name='division',
            field=models.CharField(choices=[('I', 'I'), ('II', 'II'), ('III', 'III'), ('IV', 'IV'), ('', '')], default='', max_length=5),
        ),
    ]