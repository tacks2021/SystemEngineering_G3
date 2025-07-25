# sample_app/urls.py
from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

app_name = 'sample_app'

urlpatterns = [
    # アンケートフォームページのURL
    path('questionnaire/', views.questionnaire_view, name='questionnaire'),

    # 回答完了ページのURL
    path('completion/', views.completion_view, name='completion'),

    # CSVエクスポート機能のURL
    path('export/csv/', views.export_answers_to_csv, name='export_csv'),

    # 必要であれば、回答結果を一覧表示するページのURL
    # path('results/', views.results_view, name='results'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)