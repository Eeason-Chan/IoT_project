from rest_framework.views import APIView
from rest_framework.response import Response
from .service import TrafficService


class SummaryView(APIView):
    """GET /api/traffic/summary - KPI overview"""

    def get(self, request):
        data = TrafficService.get_summary()
        return Response(data)


class DistributionView(APIView):
    """GET /api/traffic/distribution - pressure distribution"""

    def get(self, request):
        data = TrafficService.get_distribution()
        return Response(data)


class TimeseriesView(APIView):
    """GET /api/traffic/timeseries - time series trend"""

    def get(self, request):
        granularity = request.query_params.get('granularity', 'hour')
        data = TrafficService.get_timeseries(granularity)
        return Response(data)


class ZoneStatsView(APIView):
    """GET /api/traffic/zone-stats - zone ranking"""

    def get(self, request):
        data = TrafficService.get_zone_stats()
        return Response(data)


class RecordsView(APIView):
    """GET /api/traffic/records - paginated data table"""

    def get(self, request):
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        sort = request.query_params.get('sort', 'record_id')
        data = TrafficService.get_records_paginated(page, page_size, sort)
        return Response(data)