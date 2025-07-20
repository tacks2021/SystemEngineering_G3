# sample_app/views.py

import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Question, Choice, Submission, Answer # 正しいモデルをインポート

# アンケート表示・回答処理ビュー
def questionnaire_view(request):
    questions = Question.objects.all()
    if request.method == 'POST':
        submission = Submission.objects.create()

        for question in questions:
            answer_value = request.POST.get(f'answer_for_question_{question.id}')
            
            if answer_value:
                # 選択式の質問の場合
                if question.question_type == 'CHOICE':
                    # 送信された値（choice.id）からChoiceオブジェクトを取得して保存
                    selected_choice = Choice.objects.get(pk=answer_value)
                    Answer.objects.create(
                        submission=submission,
                        question=question,
                        choice=selected_choice 
                    )
                # 自由記述の質問の場合
                elif question.question_type == 'TEXT':
                    Answer.objects.create(
                        submission=submission,
                        question=question,
                        content=answer_value
                    )

        return redirect('sample_app:completion')

    return render(request, 'sample_app/questionnaire.html', {'questions': questions})

# 回答完了ページ表示ビュー
def completion_view(request):
    return render(request, 'sample_app/completion.html')

# CSVエクスポートビュー
def export_answers_to_csv(request):
    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="questionnaire_answers.csv"'},
    )
    response.write('\ufeff'.encode('utf8'))

    writer = csv.writer(response)

    questions = Question.objects.order_by('order')
    header = ['送信日時'] + [q.text for q in questions]
    writer.writerow(header)

    submissions = Submission.objects.prefetch_related('answers__question').order_by('created_at')

    for submission in submissions:
        answers_dict = {ans.question_id: ans.content for ans in submission.answers.all()}
        row = [submission.created_at.strftime("%Y-%m-%d %H:%M:%S")]
        for q in questions:
            row.append(answers_dict.get(q.id, ''))
        writer.writerow(row)

    return response

def index(request):
    return redirect('sample_app:questionnaire')