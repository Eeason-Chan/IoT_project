from django.db import models


class TrafficRecord(models.Model):
    """Traffic record after cleaning and feature engineering."""
    record_id = models.AutoField(primary_key=True)
    traffic_density = models.FloatField()
    horn_events_per_min = models.FloatField()
    avg_speed = models.FloatField()
    signal_wait_time = models.FloatField()
    weather_condition = models.CharField(max_length=20)
    road_quality_score = models.FloatField()
    driver_experience_level = models.CharField(max_length=20)
    stress_index = models.FloatField()

    # Engineered features
    hour = models.IntegerField(null=True, blank=True)
    day_of_week = models.IntegerField(null=True, blank=True)
    is_weekend = models.BooleanField(default=False)
    stress_level = models.CharField(max_length=10)  # Low, Medium, High

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'traffic_record'
        ordering = ['record_id']

    def __str__(self):
        return f"Record {self.record_id}: stress={self.stress_index}"