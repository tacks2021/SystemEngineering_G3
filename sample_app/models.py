from django.db import models

class Question(models.Model):
    # 質問タイプを定義
    QUESTION_TYPES = [
        ('TEXT', '自由記述'),
        ('CHOICE', '選択式'),
    ]
    text = models.CharField("質問文", max_length=255)
    question_type = models.CharField("質問タイプ", max_length=10, choices=QUESTION_TYPES, default='TEXT')
    order = models.PositiveIntegerField("表示順", default=0, db_index=True)

    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.text

# 選択式の質問に対する選択肢を管理するモデル
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices", verbose_name="対象の質問")
    text = models.CharField("選択肢の文言", max_length=100)

    def __str__(self):
        return self.text

class Submission(models.Model):
    created_at = models.DateTimeField("送信日時", auto_now_add=True)
    
    def __str__(self):
        return f'{self.created_at.strftime("%Y-%m-%d %H:%M:%S")} の回答'

class Answer(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="answers", verbose_name="回答セット")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="対象の質問")
    # 選択式の回答を保存するフィールド（nullを許可）
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True, verbose_name="選択した回答")
    # 自由記述の回答を保存するフィールド（nullを許可）
    content = models.TextField("自由記述の回答", null=True, blank=True)