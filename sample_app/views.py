# sample_app/views.py

import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Question, Choice, Submission, Answer


# アンケート表示・回答処理ビュー (変更なし)
def questionnaire_view(request):
    questions = Question.objects.all()
    if request.method == 'POST':
        submission = Submission.objects.create()

        for question in questions:
            answer_value = request.POST.get(f'answer_for_question_{question.id}')

            # 表示されていて、かつ値が送信された質問のみ回答を保存
            if answer_value:
                # 選択式の質問の場合
                if question.question_type == 'CHOICE':
                    try:
                        selected_choice = Choice.objects.get(pk=answer_value)
                        Answer.objects.create(
                            submission=submission,
                            question=question,
                            choice=selected_choice
                        )
                    except Choice.DoesNotExist:
                        # 不正な値が送信された場合は無視する
                        pass
                # 自由記述の質問の場合
                elif question.question_type == 'TEXT':
                    Answer.objects.create(
                        submission=submission,
                        question=question,
                        content=answer_value
                    )

        return redirect('sample_app:completion')

    return render(request, 'sample_app/questionnaire.html', {'questions': questions})


# 回答完了ページ表示ビュー (変更なし)
def completion_view(request):
    return render(request, 'sample_app/completion.html')


# ▼▼▼ CSVエクスポートビュー (修正版) ▼▼▼
def export_answers_to_csv(request):
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="questionnaire_answers.csv"'},
    )
    # BOMを追加してExcelでの文字化けを防ぐ
    response.write('\ufeff'.encode('utf8'))

    writer = csv.writer(response)

    # ヘッダー行の作成
    questions = Question.objects.order_by('order')
    header = ['送信日時'] + [q.text for q in questions]
    writer.writerow(header)

    # prefetch_relatedでデータベースへのアクセスを効率化
    submissions = Submission.objects.prefetch_related('answers', 'answers__question', 'answers__choice').order_by(
        'created_at')

    for submission in submissions:
        # 回答を質問IDをキーにした辞書に格納
        answers_dict = {ans.question_id: ans for ans in submission.answers.all()}

        row = [submission.created_at.strftime("%Y-%m-%d %H:%M:%S")]

        for q in questions:
            answer = answers_dict.get(q.id)
            if answer:
                # 選択式の回答があればそのテキストを、なければ自由記述の回答を出力
                if answer.choice:
                    row.append(answer.choice.text)
                else:
                    row.append(answer.content)
            else:
                # 回答がなければ空文字を追加
                row.append('')
        writer.writerow(row)

    return response

def survey_view(request):
    table_question_texts = [
        "金額", "スペース", "評価方法", 
        "メンテナンス", "重さ", "フィードバック", "人工呼吸"
    ]
    
    # orderフィールドの昇順で取得
    table_questions = Question.objects.filter(
        text__in=table_question_texts
    ).order_by('order') 
    
    # こちらもorderフィールドの昇順で取得
    other_questions = Question.objects.exclude(
        text__in=table_question_texts
    ).order_by('order')
    
    context = {
        'main_question_text': "...",
        'table_questions': table_questions,
        'other_questions': other_questions
    }
    return render(request, 'sample_app/survey_form.html', context)

def index(request):
    return redirect('sample_app:questionnaire')
