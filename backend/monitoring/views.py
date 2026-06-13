from rest_framework.views import APIView
from rest_framework.response import Response
from .service import MonitoringService


class HealthView(APIView):
    """GET /api/system/health - Health check"""

    def get(self, request):
        data = MonitoringService.health_check()
        status = 200 if data.get('status') == 'healthy' else 503
        return Response(data, status=status)


class StatsView(APIView):
    """GET /api/system/stats - Data statistics"""

    def get(self, request):

        return 
