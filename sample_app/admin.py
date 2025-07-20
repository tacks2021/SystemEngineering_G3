# sample_app/admin.py

from django.contrib import admin
from .models import Question, Choice, Submission, Answer

# Questionモデルの管理画面表示をカスタマイズ
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2 # デフォルトで表示する選択肢の入力欄の数

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'question_type', 'order')
    list_filter = ('question_type',)
    # Questionの編集ページにChoiceInlineを組み込む
    inlines = [ChoiceInline]

# Submissionモデルの管理画面表示をカスタマイズ
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
    readonly_fields = ('created_at',)

# Answerモデルの管理画面表示をカスタマイズ
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'choice', 'content', 'submission')


# 各モデルを管理画面に登録
admin.site.register(Question, QuestionAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Answer, AnswerAdmin)