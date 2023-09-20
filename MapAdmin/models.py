from django.db import models
#from django.contrib.gis.db import models
# Create your models here.

# Puntos del mapa que se usan como conexion entre caminos
class Punto(models.Model):
    lat = models.DecimalField(max_digits=12, decimal_places=10)
    lon = models.DecimalField(max_digits=12, decimal_places=10)
# Linea que hace constituida de puntos para hacer de camino (este es visual)
    def __str__(self):
        return str(self.lat)+','+str(self.lon)
class Linea(models.Model):
    punto_inicio = models.ForeignKey(Punto, on_delete=models.CASCADE, related_name='punto_inicio')
    punto_fin = models.ForeignKey(Punto, on_delete=models.CASCADE, related_name='punto_fin')
    peso = models.FloatField()
# Edificio o Sala de clases, este hace referencia a las edificaciones de la Universidad
class Edificacion(models.Model):
    nombre = models.CharField(max_length=50)
    piso = models.IntegerField()
    pertenece = models.ForeignKey('self', on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return f"{self.nombre} -- {self.pertenece.nombre}" if self.pertenece else self.nombre

class EntradasEdificacion(models.Model):
    edificio = models.ForeignKey(Edificacion, on_delete=models.CASCADE,related_name='edificio')
    punto_camino = models.ForeignKey(Punto, on_delete=models.CASCADE,related_name='punto_camino')
    def __str__(self):
        return self.edificio.nombre +"---("+ str(self.punto_camino.lat)+','+str(self.punto_camino.lon)+")"

# Puntos que definen la estructura de un edificio
class EstructuraEdificacion(models.Model):
    edificacion = models.ForeignKey(Edificacion, on_delete=models.CASCADE)
    lat = models.DecimalField(max_digits=12, decimal_places=10)
    lon = models.DecimalField(max_digits=12, decimal_places=10)




"""
# Carrera hace referencia a las carreras que son de la universidad
class Carrera(models.Model):
    nombre = models.CharField(max_length=50)
    edificio = models.ForeignKey(Edificio, on_delete=models.SET_NULL, null=True)

# Informacion sobre edificio o carrera
class Informacion(models.Model):
    nombre = models.TextField(max_length=50)
    edificio = models.ForeignKey('Edificio', on_delete=models.SET_NULL, null=True)
    carrera = models.ForeignKey('Carrera', on_delete=models.SET_NULL, null=True)

class Telefono(models.Model):
    numero = models.CharField(max_length=50)
    informacion = models.ForeignKey('Informacion', on_delete=models.SET_NULL, null=True)

class Detalle(models.Model):
    parrafos = models.TextField(max_length=3000)
    informacion = models.ForeignKey('Informacion', on_delete=models.CASCADE)

"""