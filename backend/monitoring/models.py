from django.db import models


class MonitoringStats(models.Model):
    """System monitoring statistics."""
    id = models.AutoField(primary_key=True)
    record_count = models.IntegerField(default=0)
    zone_count = models.IntegerField(default=0)
    time_range_start = models.DateTimeField(null=True, blank=True)
    time_range_end = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'monitoring_stats'

    def __str__(self):
        return f"Stats: {self.record_count} records"