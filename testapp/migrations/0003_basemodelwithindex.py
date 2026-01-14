# Migration for issue #58 - indexes on TypedModel base classes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testapp', '0002_developer_employee_manager'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseModelWithIndex',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('testapp.submodela', 'Sub Model A'), ('testapp.submodelb', 'Sub Model B')], db_index=True, max_length=255)),
                ('name', models.CharField(max_length=100)),
                ('tag', models.CharField(max_length=100)),
                ('field_a', models.CharField(max_length=100, null=True)),
                ('field_b', models.IntegerField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddIndex(
            model_name='basemodelwithindex',
            index=models.Index(fields=['tag'], name='testapp_bas_tag_f26b85_idx'),
        ),
        migrations.CreateModel(
            name='SubModelA',
            fields=[
            ],
            options={
                'verbose_name': 'Sub Model A',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('testapp.basemodelwithindex',),
        ),
        migrations.CreateModel(
            name='SubModelB',
            fields=[
            ],
            options={
                'verbose_name': 'Sub Model B',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('testapp.basemodelwithindex',),
        ),
    ]
