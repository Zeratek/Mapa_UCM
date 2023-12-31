# Generated by Django 4.2 on 2023-09-23 20:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Edificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('piso', models.IntegerField()),
                ('pertenece', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='MapAdmin.edificacion')),
            ],
        ),
        migrations.CreateModel(
            name='Punto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lat', models.DecimalField(decimal_places=10, max_digits=12)),
                ('lon', models.DecimalField(decimal_places=10, max_digits=12)),
            ],
        ),
        migrations.CreateModel(
            name='Linea',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('peso', models.FloatField()),
                ('punto_fin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='punto_fin', to='MapAdmin.punto')),
                ('punto_inicio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='punto_inicio', to='MapAdmin.punto')),
            ],
        ),
        migrations.CreateModel(
            name='EstructuraEdificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lat', models.DecimalField(decimal_places=10, max_digits=12)),
                ('lon', models.DecimalField(decimal_places=10, max_digits=12)),
                ('edificacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='MapAdmin.edificacion')),
            ],
        ),
        migrations.CreateModel(
            name='EntradasEdificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('edificio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='edificio', to='MapAdmin.edificacion')),
                ('punto_camino', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='punto_camino', to='MapAdmin.punto')),
            ],
        ),
    ]
