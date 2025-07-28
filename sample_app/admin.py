# sample_app/admin.py

import csv
from django.http import HttpResponse
from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from .graph import create_comparison_chart
from .models import Question, Choice, Submission, Answer
import json
import io
import base64
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import numpy as np
import japanize_matplotlib

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
        extra_context = extra_context or {}
        categories = ["人工呼吸", "フィードバック", "重さ", "メンテナンス", "評価方法", "スペース", "金額"]
        choice1_text = 'マネキン'
        choice2_text = 'VR'

        group1_counts = []
        group2_counts = []

        for category_text in categories:
            question = Question.objects.filter(text=category_text).first()
            # 質問がデータベースに存在する場合
            
            if question:
                # その質問に対して「マネキン」と回答された数をカウント
                count1 = Answer.objects.filter(question=question, choice__text=choice1_text).count()
                
                # その質問に対して「VR」と回答された数をカウント
                count2 = Answer.objects.filter(question=question, choice__text=choice2_text).count()
                
                group1_counts.append(count1)
                group2_counts.append(count2)
            else:
                # 質問がデータベースに存在しない場合は、グラフが崩れないように0を追加
                group1_counts.append(0)
                group2_counts.append(0)

        # =================================================================
        # 2. graph.pyの関数を呼び出してグラフ画像を生成
        # =================================================================
        # 以前の長いMatplotlibのコードが、この1行に置き換わる！
        chart_image_base64 = create_comparison_chart(
            categories, 
            group1_counts, 
            group2_counts,
            choice1_text, # ラベル用にテキストも渡す
            choice2_text
        )
        
        # extra_contextに画像データを追加
        extra_context['matplotlib_chart'] = chart_image_base64
        
        return super().changelist_view(request, extra_context=extra_context)

# 各モデルを管理画面に登録
admin.site.register(Question, QuestionAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Choice)