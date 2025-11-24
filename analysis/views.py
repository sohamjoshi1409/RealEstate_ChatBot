# analysis/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, parsers
from django.conf import settings
import os

from .utils import (
    load_dataset, parse_query_text, filter_by_area,
    chart_data_for_area, build_mock_summary
)

class UploadDatasetView(APIView):
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request, format=None):
        f = request.FILES.get('file')
        if not f:
            return Response({"error": "No file uploaded under key 'file'."}, status=status.HTTP_400_BAD_REQUEST)

        # Save to upload dir defined in settings.MEDIA_ROOT
        save_dir = getattr(settings, 'MEDIA_ROOT', None) or os.path.join(settings.BASE_DIR, 'uploaded_files')
        os.makedirs(save_dir, exist_ok=True)

        import uuid
        fn = f"{uuid.uuid4().hex}_{f.name}"
        full = os.path.join(save_dir, fn)
        with open(full, 'wb') as dest:
            for chunk in f.chunks():
                dest.write(chunk)

        return Response({"uploaded_path": full}, status=status.HTTP_201_CREATED)

class QueryAnalysisView(APIView):
    """
    POST payload:
    {
      "query": "Analyze Wakad",
      "use_preloaded": true,
      "preloaded_path": null,
      "uploaded_path": null
    }
    """
    def post(self, request, format=None):
        body = request.data
        query = body.get('query') or body.get('q') or ''
        if not query:
            return Response({"error": "No query provided."}, status=status.HTTP_400_BAD_REQUEST)

        use_preloaded = bool(body.get('use_preloaded', True))
        preloaded_path = body.get('preloaded_path')
        uploaded_path = body.get('uploaded_path')

        dataset_path = None
        if uploaded_path:
            dataset_path = uploaded_path
        elif not use_preloaded:
            return Response({"error": "No dataset provided and use_preloaded is false."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            dataset_path = preloaded_path  # may be None and load_dataset will use SAMPLE_EXCEL_PATH

        try:
            df = load_dataset(dataset_path)
        except Exception as e:
            return Response({"error": f"Failed to load dataset: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        parsed = parse_query_text(query)
        intent = parsed.get('intent')
        areas = parsed.get('areas', [])
        last_n = parsed.get('last_n_years')

        if intent == 'compare' and len(areas) >= 2:
            results = {}
            for a in areas:
                chart = chart_data_for_area(df, a, last_n_years=last_n)
                filtered = filter_by_area(df, [a]).head(200)
                summary = build_mock_summary(filtered, a)
                results[a] = {
                    "summary": summary,
                    "chart": chart,
                    "table": filtered.fillna('').to_dict(orient='records')
                }
            return Response({"type": "compare", "results": results})

        area = areas[0] if areas else None
        if not area:
            return Response({"error": "Could not identify an area from the query."}, status=status.HTTP_400_BAD_REQUEST)

        filtered_df = filter_by_area(df, [area]).head(1000)
        chart = chart_data_for_area(df, area, last_n_years=last_n)
        summary = build_mock_summary(filtered_df, area)
        table_json = filtered_df.fillna('').to_dict(orient='records')

        return Response({
            "type": "single",
            "area": area,
            "summary": summary,
            "chart": chart,
            "table": table_json
        })
