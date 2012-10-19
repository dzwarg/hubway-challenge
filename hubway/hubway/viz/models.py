from django.db import models

# Create your models here.
class Trip(models.Model):
    id = models.IntegerField(primary_key=True)
    status = models.TextField()
    duration = models.IntegerField()
    start_date = models.DateTimeField()
    start_station_id = models.IntegerField()
    end_date = models.DateTimeField()
    end_station_id = models.IntegerField()
    bike_nr = models.TextField()
    subscription_type = models.TextField()
    zip_code = models.TextField()
    birth_date = models.IntegerField(null=True)
    gender = models.TextField()

    class Meta:
        db_table = 'trips'
