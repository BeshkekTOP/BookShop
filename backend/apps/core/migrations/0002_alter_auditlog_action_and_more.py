# Generated manually for improved audit system
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='auditlog',
            options={'ordering': ['-created_at']},
        ),
        migrations.RemoveField(
            model_name='auditlog',
            name='actor',
        ),
        migrations.AddField(
            model_name='auditlog',
            name='action',
            field=models.CharField(
                choices=[
                    ('created', 'Создано'),
                    ('updated', 'Обновлено'),
                    ('deleted', 'Удалено'),
                    ('viewed', 'Просмотрено')
                ],
                default='viewed',
                max_length=100
            ),
        ),
        migrations.AddField(
            model_name='auditlog',
            name='actor',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='audit_logs',
                to='auth.user'
            ),
        ),
        migrations.AddField(
            model_name='auditlog',
            name='content_type',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='contenttypes.contenttype'
            ),
        ),
        migrations.AddField(
            model_name='auditlog',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='auditlog',
            name='new_data',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='auditlog',
            name='object_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='auditlog',
            name='old_data',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='auditlog',
            name='user_agent',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='auditlog',
            name='method',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AlterField(
            model_name='auditlog',
            name='path',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]

