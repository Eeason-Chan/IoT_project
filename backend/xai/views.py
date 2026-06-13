from rest_framework.views import APIView
from rest_framework.response import Response
from traffic.service import TrafficService
from .service import SHAPService, LIMEService
from .models import SHAPGlobal, SHAPLocal, LIMELocal


class SHAPGlobalView(APIView):
    """GET /api/xai/shap/global - Global feature importance"""

    def get(self, request):
        records = TrafficService.get_all_records_for_xai()
        if not records:
            return Response({'error': 'No data'}, status=404)

        # Check if already computed
        global_data = SHAPGlobal.objects.all()
        if global_data.exists():
            data = [{'feature': g.feature, 'shap_value': g.shap_value} for g in global_data]
        else:
            data = SHAPService.compute_global(records)

        return Response({'features': data})


class SHAPLocalView(APIView):
    """GET /api/xai/shap/local/<record_id> - Single record SHAP explanation"""

    def get(self, request, record_id):
        records = TrafficService.get_all_records_for_xai()
        local = SHAPService.compute_local(record_id)
        if local is None:
            # Compute on demand if not in DB
            local = SHAPService.compute_local_on_demand(record_id, records)
        if local is None:
            return Response({'error': 'Record not found'}, status=404)
        return Response({'record_id': record_id, 'shap_values': local})


class SHAPSummaryView(APIView):
    """GET /api/xai/shap/summary - SHAP summary scatter plot"""

    def get(self, request):
        records = TrafficService.get_all_records_for_xai()
        data = SHAPService.get_summary_scatter(records)
        return Response({'data': data})


class LIMELocalView(APIView):
    """GET /api/xai/lime/local/<record_id> - Single record LIME explanation"""

    def get(self, request, record_id):
        record_id = int(record_id)
        records = TrafficService.get_all_records_for_xai()

        # Try cache first
        lime_data = LIMEService.get_local(record_id)
        if lime_data is None:
            lime_data = LIMEService.compute_local(record_id, records)

        if lime_data is None:
            return Response({'error': 'Record not found'}, status=404)

        return Response({'record_id': record_id, 'lime_weights': lime_data})


class CompareView(APIView):
    """GET /api/xai/compare/<record_id> - SHAP vs LIME comparison"""

    def get(self, request, record_id):
        record_id = int(record_id)
        records = TrafficService.get_all_records_for_xai()

        shap_local = SHAPService.compute_local(record_id)
        lime_local = LIMEService.get_local(record_id)

        if lime_local is None:
            lime_local = LIMEService.compute_local(record_id, records)

        if shap_local is None:
            return Response({'error': 'Record not found'}, status=404)

        return Response({
            'record_id': record_id,
            'shap': shap_local,
            'lime': lime_local
        })