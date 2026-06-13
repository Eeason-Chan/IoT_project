"""
Monitoring Service - health check and data statistics.
"""
from django.db import connection
from traffic.models import TrafficRecord
from .models import MonitoringStats


class MonitoringService:
    """System monitoring operations."""

    @staticmethod
    def health_check():
        """Check Django and MySQL connectivity."""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return {'status': 'healthy', 'django': 'ok', 'mysql': 'ok'}
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}

    @staticmethod
    def get_stats():
        """Get data statistics."""
        total = TrafficRecord.objects.count()
        zones = TrafficRecord.objects.values('road_quality_score').distinct().count()
        records = TrafficRecord.objects.all()

        hours = set()
        for r in records:
            if r.hour is not None:
                hours.add(r.hour)

        time_range = {}
        if records:
            time_range = {'start': 'Hour 0', 'end': f'Hour {max(hours)}' if hours else 'Hour 23'}

        # Update monitoring stats
        MonitoringStats.objects.all().delete()
        MonitoringStats.objects.create(
            record_count=total,
            zone_count=zones,
        )

        return {
            'record_count': total,
            'zone_count': zones,
            'time_range': time_range
        }