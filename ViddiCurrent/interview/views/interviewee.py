from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views.generic import (ListView, TemplateView)
from django.http import HttpResponse
from ..decorators import user_role_is_required
from django.shortcuts import get_object_or_404, redirect, render

from ..models import (TakenInterview, Review, Settings, PracticeInterview, Interviewee, Answer)
from django.utils import timezone
import datetime
import json
from django.core.mail import send_mail
from django.conf import settings


class HomePageView(TemplateView):
    template_name = 'index.html'


@method_decorator([login_required, user_role_is_required(role_is=10)], name='dispatch')
class CandidateInterviewListView(ListView):
    model = TakenInterview
    context_object_name = 'candidate_interviews'
    template_name = 'interview/interviewee/user_dashboard.html'

    def get_queryset(self):
        if self.request.user.user_type == 10:
            queryset = self.request.user.user_for_interview.candidate.filter(status__in=[1, 2])
        else:
            queryset = TakenInterview.objects.none()
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(CandidateInterviewListView, self).get_context_data(**kwargs)
        pi = PracticeInterview.objects.filter(
            status__in=[103],
            candidate__user_for_interview__email=self.request.user.email)
        if len(pi) > 0:
            practice_flag = False
        else:
            practice_flag = True
        context['practice_flag'] = practice_flag
        return context


@login_required
@user_role_is_required(role_is=10)
def interviewee_interview(request, *args, **kwrgs):
    if request.user.user_type == 10:
        interview_instance = TakenInterview.objects.filter(id=kwrgs['pk'], status__in=[1, 2],
                                                           candidate__user_for_interview__email=request.user.email)
        if len(interview_instance) > 0:
            interview_instance = interview_instance[0]
            queryArray = dict()
            totalquestion = len(interview_instance.answers.filter(video_id=''))
            if totalquestion > 0:
                qu_json = []
                for index, qu in enumerate(interview_instance.answers.filter(video_id='').order_by('index')):
                    qu_json.append([str(qu.question.text), int(qu.question.time), int(qu.question.id)])
                queryArray["COLUMNS"] = ["QUESTION", "TIMEOUT", "QUESTIONID"]
                queryArray["DATA"] = qu_json
                queryArray = json.dumps(queryArray)
            else:
                interview_instance.status = 3
                interview_instance.save()
                messages.error(request, 'Congratulations, You have completed the video interview. We will be in touch shortly. Thank you.')
                return redirect('interviewee:dashboard')
        else:
            messages.error(request, 'User rights required!')
            return redirect('interviewee:dashboard')
    else:
        response = HttpResponse('Page not found', status=404)
        response['Content-Length'] = len(response.content)
        return response

    if request.is_ajax():
        if isinstance(interview_instance, TakenInterview):
            if 'candidate_ID' in request.GET and 'interview_ID' in request.GET and 'question_ID' in request.GET \
                    and 'location' in request.GET and 'video_name' in request.GET and 'videoId' in request.GET:
                if int(request.GET['interview_ID']) != kwrgs['pk'] or int(
                        request.GET['candidate_ID']) != request.user.id or int(request.GET['question_ID']) not in [
                        a['question_id'] for a in interview_instance.answers.filter(video_id='').values('question_id')]:
                    response = HttpResponse('User rights require', status=404)
                    response['Content-Length'] = len(response.content)
                    return response
                else:
                    interview_instance.status = 2
                    interview_instance.interview_attempt_date = timezone.now() #datetime.datetime.now()
                    interview_instance.save()
                    answer_instance = interview_instance.answers.filter(question__id=int(request.GET['question_ID']))[0]
                    answer_instance.video_id = str(request.GET['videoId'])
                    answer_instance.video_name = str(request.GET['video_name'])
                    answer_instance.location = str(request.GET['location'])
                    answer_instance.save()
                    response = HttpResponse('Details saved Successfully!', status=200)
                    response['Content-Length'] = len(response.content)
                    return response

            elif 'user_id' in request.GET and 'attendDate' in request.GET and 'interviewid' in request.GET:
                if int(request.GET['interviewid']) != kwrgs['pk'] or int(
                        request.GET['user_id']) != request.user.id or len(
                        interview_instance.answers.filter(video_id='')) != 0:
                    response = HttpResponse('User rights require', status=404)
                    response['Content-Length'] = len(response.content)
                    return response
                else:
                    interview_instance.status = 3
                    interview_instance.save()
                    messages.success(request, "Interview completed successfully!!")
                    return redirect('interviewee:dashboard')
        else:
            response = HttpResponse('User rights require', status=404)
            response['Content-Length'] = len(response.content)
            return response
    practice_flag = False
    return render(request, 'interview/interviewee/user_interview.html',
                  {'id': kwrgs['pk'],
                   'interview_instance': interview_instance, 'queryArray': queryArray, 'totalquestion': totalquestion,
                   'range': range(totalquestion), 'practice_flag': practice_flag})


@login_required
@user_role_is_required(role_is=10)
def interview_practice(request, *args, **kwrgs):
    if request.user.user_type == 10:
        pending_interview = len(TakenInterview.objects.filter(status__in=[1, 2],
                                                              candidate__user_for_interview__email=request.user.email))
        pending_practice = len(PracticeInterview.objects.filter(
            status__in=[103],
            candidate__user_for_interview__email=request.user.email))
        if pending_practice == 0 and pending_interview > 0:
            interview_instance = PracticeInterview.objects.filter(
                status__in=[101, 102],
                candidate__user_for_interview__email=request.user.email)
            if len(interview_instance) > 0:
                interview_instance = interview_instance[0]
            else:
                interview = Settings.objects.filter()[0].practice_interview
                interviewee = Interviewee.objects.filter(user_for_interview__email=request.user.email)[0]
                interview_instance = PracticeInterview.objects.create(
                    taken_interviews=interview,
                    candidate=interviewee,
                    status=101,
                )
                for q in interview.question_interview.filter().order_by('index'):
                    answer = interview_instance.answers.add(Answer.objects.create(
                        candidate=interviewee,
                        question=q.question,
                        text="",
                        index=q.index
                    )
                    )
            queryArray = dict()
            totalquestion = len(interview_instance.answers.filter(video_id=''))
            if totalquestion > 0:
                qu_json = []
                for index, qu in enumerate(interview_instance.answers.filter(video_id='').order_by('index')):
                    qu_json.append([str(qu.question.text), int(qu.question.time), int(qu.question.id)])
                queryArray["COLUMNS"] = ["QUESTION", "TIMEOUT", "QUESTIONID"]
                queryArray["DATA"] = qu_json
                queryArray = json.dumps(queryArray)
            else:
                interview_instance.status = 103
                interview_instance.save()
                messages.error(request, 'Congratulations, You have attempted all interviews!')
                return redirect('interviewee:dashboard')

        else:
            messages.info(request, 'You have already attempted practice questions!')
            return redirect('interviewee:dashboard')
    else:
        response = HttpResponse('Page not found', status=404)
        response['Content-Length'] = len(response.content)
        return response

    if request.is_ajax():
        if isinstance(interview_instance, PracticeInterview):
            if 'candidate_ID' in request.GET and 'interview_ID' in request.GET and 'question_ID' in request.GET \
                    and 'location' in request.GET and 'video_name' in request.GET and 'videoId' in request.GET:
                if int(request.GET['candidate_ID']) != request.user.id or int(request.GET['question_ID']) not in [
                        a['question_id'] for a in interview_instance.answers.filter(video_id='').values('question_id')]:
                    response = HttpResponse('User rights require', status=404)
                    response['Content-Length'] = len(response.content)
                    return response
                else:
                    interview_instance.status = 102
                    interview_instance.interview_attempt_date = timezone.now() #datetime.datetime.now()
                    interview_instance.save()
                    answer_instance = interview_instance.answers.filter(question__id=int(request.GET['question_ID']))[0]
                    answer_instance.video_id = str(request.GET['videoId'])
                    answer_instance.video_name = str(request.GET['video_name'])
                    answer_instance.location = str(request.GET['location'])
                    answer_instance.save()
                    response = HttpResponse('Details saved Successfully!', status=200)
                    response['Content-Length'] = len(response.content)
                    return response

            elif 'user_id' in request.GET and 'attendDate' in request.GET and 'interviewid' in request.GET:
                if int(request.GET['interviewid']) != kwrgs['pk'] or int(
                        request.GET['user_id']) != request.user.id or len(
                        interview_instance.answers.filter(video_id='')) != 0:
                    response = HttpResponse('User rights require', status=404)
                    response['Content-Length'] = len(response.content)
                    return response
                else:
                    interview_instance.status = 3
                    interview_instance.save()
                    messages.success(request, "Interview completed successfully!!")
                    return redirect('interviewee:dashboard')
        else:
            response = HttpResponse('User rights require', status=404)
            response['Content-Length'] = len(response.content)
            return response
    practice_flag = True
    return render(request, 'interview/interviewee/user_interview.html',
                  {'id': interview_instance.id,
                   'interview_instance': interview_instance, 'queryArray': queryArray, 'totalquestion': totalquestion,
                   'range': range(totalquestion), 'practice_flag': practice_flag})
