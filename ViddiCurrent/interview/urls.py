from django.urls import include, path

from .views import interview, interviewee, interviewer
from .views import *
urlpatterns = [
    path('home/', interview.home, name='home'),
    path('interviewer/', include(([
         path('', interviewer.manage_dashboard, name='dashboard'),

         path('users/', interviewer.UserManagementListView.as_view(),
              name='user_management_list'),
         path('users/add/', interviewer.InterviewerSignUpView.as_view(),
              name='user_management_add'),
         path('users/<int:pk>/', interviewer.InterviewerUpdateView.as_view(),
              name='user_management_edit'),
         path('users/<int:pk>/delete/', interviewer.InterviewerDeleteView.as_view(),
              name='user_management_delete'),

         path('company/', interviewer.CompanyListView.as_view(), name='company_list'),
         path('company/add/', interviewer.CompanyCreateView.as_view(),
              name='company_add'),
         path('company/email/<int:pk>',
              interviewer.CompanyEmailView.as_view(), name='company_email'),
         path('company/<int:pk>/edit',
              interviewer.CompanyUpdateView.as_view(), name='company_edit'),
         path('company/<int:pk>/delete/',
              interviewer.CompanyDeleteView.as_view(), name='company_delete'),

         path('questions/', interviewer.QuestionListView.as_view(),
              name='questions_list'),
         path('questions/add/', interviewer.QuestionCreateView.as_view(),
              name='question_add'),
         path('questions/<int:pk>/',
              interviewer.QuestionUpdateView.as_view(), name='question_edit'),
         path('questions/<int:pk>/delete/',
              interviewer.QuestionDeleteView.as_view(), name='question_delete'),

         path('vacancies/', interviewer.VacancyListView.as_view(),
              name='vacancies_list'),
         path('vacancies/add/', interviewer.VacancyCreateView.as_view(),
              name='vacancy_add'),
         path('vacancies/<int:pk>/',
              interviewer.VacancyUpdateView.as_view(), name='vacancy_edit'),
         path('vacancies/<int:pk>/delete/',
              interviewer.VacancyDeleteView.as_view(), name='vacancy_delete'),

         path('interviews/', interviewer.InterviewListView.as_view(),
              name='interviews_list'),
         path('interviews/add/', interviewer.InterviewCreateView.as_view(),
              name='interview_add'),
         path('interviews/<int:pk>/',
              interviewer.InterviewUpdateView.as_view(), name='interview_edit'),
         path('interviews/<int:pk>/delete/',
              interviewer.InterviewDeleteView.as_view(), name='interview_delete'),
         path('interviews/<int:pk>/candidate/add/',
              interviewer.interviewee_create, name='interviewee_add'),
         path('interviews/<int:pk>/candidates/all/', interviewer.InterviewCandidateListView.as_view(),
              name='interview_candidates_list'),
         path('interviews/<int:pk>/candidates/complete/', interviewer.InterviewCompleteCandidateListView.as_view(),
              name='interview_complete_candidates_list'),
         path('interviews/<int:interview_pk>/candidate/<int:candidate_pk>/', interviewer.interviewee_review,
              name='interviewee_review'),

         path('candidates/', interviewer.CandidateListView.as_view(),
              name='candidates_list'),
         path('candidates/<int:pk>/delete/',
              interviewer.CandidateDeleteView.as_view(), name='candidate_delete'),

         path('settings/', interviewer.manage_settings, name='settings'), ], 'interview'), namespace='interviewer')),

    path('interviewee/', include(([

        path('', interviewee.CandidateInterviewListView.as_view(), name='dashboard'),
        path('interview/<int:pk>/', interviewee.interviewee_interview,
             name='interviewee_attempt'),
        path('interview/practice/', interviewee.interview_practice, name='interview_practice'), ], 'interview'), namespace='interviewee')),
]
