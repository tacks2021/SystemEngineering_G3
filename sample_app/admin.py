# sample_app/admin.py

import csv
from django.http import HttpResponse
from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from .models import Question, Choice, Submission, Answer
import json

# --- Submission用エクスポートアクション ---
def export_submissions_as_csv(modeladmin, request, queryset):
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="submissions.csv"'},
    )
    response.write('\ufeff'.encode('utf8'))
    writer = csv.writer(response)

    questions = Question.objects.order_by('order')
    header = ['送信日時'] + [q.text for q in questions]
    writer.writerow(header)

    for submission in queryset.prefetch_related('answers__question', 'answers__choice'):
        answers_dict = {}
        for ans in submission.answers.all():
            # 選択式か自由記述かで保存する内容を分ける
            if ans.choice:
                answers_dict[ans.question_id] = ans.choice.text
            else:
                answers_dict[ans.question_id] = ans.content

        row = [submission.created_at.strftime("%Y-%m-%d %H:%M:%S")]
        for q in questions:
            row.append(answers_dict.get(q.id, ''))
        writer.writerow(row)

    return response
export_submissions_as_csv.short_description = "選択された回答セットをCSVエクスポート(横長形式)"

# --- ここからAnswer用エクスポートアクション ---
def export_answers_as_csv(modeladmin, request, queryset):
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="answers.csv"'},
    )
    response.write('\ufeff'.encode('utf8'))
    writer = csv.writer(response)
    
    # ヘッダー行を作成
    header = ['回答ID', '送信日時', '質問文', '回答内容']
    writer.writerow(header)

    # データ行を作成 (選択されたAnswerオブジェクトをループ)
    for answer in queryset.select_related('submission', 'question', 'choice'):
        # 選択式か自由記述かで回答内容を決定
        if answer.choice:
            answer_content = answer.choice.text
        else:
            answer_content = answer.content

        row = [
            answer.id,
            answer.submission.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            answer.question.text,
            answer_content
        ]
        writer.writerow(row)
    
    return response
export_answers_as_csv.short_description = "選択された個別回答をCSVエクスポート(縦長形式)"
# --- ここまで ---

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'question_type', 'order')
    list_filter = ('question_type',)
    inlines = [ChoiceInline]

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'display_answers') # display_answersを追加
    readonly_fields = ('created_at',)
    actions = [export_submissions_as_csv]

    # 回答内容を一覧に表示するためのカスタムメソッド
    def display_answers(self, obj):
        # Submissionに紐づく全てのAnswerを取得
        answers = obj.answers.select_related('question', 'choice').all()
        lines = []
        for ans in answers:
            # 選択式か自由記述かで表示するテキストを決定
            answer_text = ans.choice.text if ans.choice else ans.content
            # HTMLとして整形
            lines.append(f"<b>{ans.question.text}</b>: {answer_text}")
        return format_html("<br>".join(lines))
    
    # 管理画面での列のヘッダー名を指定
    display_answers.short_description = '回答概要'

class AnswerAdmin(admin.ModelAdmin):
    change_list_template = "sample_app/change_list.html"
    list_display = ('id', 'question', 'choice', 'submission')
    actions = [export_answers_as_csv] # ← ここでAnswer用アクションを登録
    # 回答内容で検索できるようにする
    search_fields = ['content', 'choice__text']

    # 一覧表示ページ(change_list)の処理を上書き
    def changelist_view(self, request, extra_context=None):
        # 回答を集計する質問を特定（例としてID=1の質問）
        TARGET_QUESTION_ID = 1

        # 質問の各選択肢(Choice)が、それぞれ何回答(Answer)されたかを集計
        chart_data_queryset = Choice.objects.filter(question_id=TARGET_QUESTION_ID).annotate(
            answer_count=Count('answer')
        ).values('text', 'answer_count')
        
        # テンプレートに渡すためにデータを整形
        chart_labels = [item['text'] for item in chart_data_queryset]
        chart_data = [item['answer_count'] for item in chart_data_queryset]

        # extra_contextに集計データを追加
        extra_context = extra_context or {}
        # json.dumpsでJavaScriptが安全に読み込める形式に変換
        extra_context['chart_labels'] = json.dumps(chart_labels)
        extra_context['chart_data'] = json.dumps(chart_data)
        
    def changelist_view(self, request, extra_context=None):
        # 質問タイプが「選択式」の質問をすべて取得
        choice_questions = Question.objects.filter(question_type='CHOICE')

        # 各質問のグラフデータを格納するリスト
        charts_data = []

        for question in choice_questions:
            # 質問ごとに回答を集計
            chart_data_queryset = Choice.objects.filter(question=question).annotate(
                answer_count=Count('answer')
            ).values('text', 'answer_count')
            
            labels = [item['text'] for item in chart_data_queryset]
            data = [item['answer_count'] for item in chart_data_queryset]

            # グラフ1つ分のデータを辞書として追加
            charts_data.append({
                'question_text': question.text,
                'labels': labels,
                'data': data,
            })

        extra_context = extra_context or {}
        # グラフデータのリストをJSON形式でテンプレートに渡す
        extra_context['charts_data'] = json.dumps(charts_data)
        
        return super().changelist_view(request, extra_context=extra_context)

# 各モデルを管理画面に登録
admin.site.register(Question, QuestionAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Choice)