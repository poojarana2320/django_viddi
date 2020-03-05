from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (CreateView, DeleteView, ListView,
                                  UpdateView, TemplateView)
from django.contrib.auth.mixins import LoginRequiredMixin
from ..decorators import user_role_less_than_required
from ..forms import (InterviewerSignUpForm, InterviewerUpdateForm, CompanyCreateForm, CompanyUpdateForm, CompanyEmailForm, QuestionCreateForm, QuestionUpdateForm,
                     VacancyCreateForm, VacancyUpdateForm, InterviewCreateForm, InterviewUpdateForm,
                     IntervieweeSignUpForm, )
from ..models import (User, Company, Interviewer, Interviewee, Question, Vacancy, Interview,
                      TakenInterview, Review, Answer, Settings)
import datetime
import json
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.db.models import Count
from turborecruit.settings import ADMIN_COMPANY_NAME


class HomePageView(TemplateView):
    template_name = 'interview/interviewer/dashboard.html'


@method_decorator([login_required, user_role_less_than_required(role_less_than=3)], name='dispatch')
class InterviewerSignUpView(LoginRequiredMixin, CreateView):
    model = User
    form_class = InterviewerSignUpForm
    template_name = 'interview/interviewer/user_management_create.html'

    def form_valid(self, form):
        if self.request.user.user_type == 1:
            user = form.save(user_obj=self.request.user)
            messages.success(self.request, 'User was added successfully')
            return redirect('interviewer:user_management_list')
        elif self.request.user.user_type == 2 \
                and "user_type=1" not in str(self.request.body):
            user = form.save(user_obj=self.request.user)
            messages.success(self.request, 'User was added successfully')
            return redirect('interviewer:user_management_list')
        messages.error(
            self.request, 'You need permission to perform this action')
        return redirect('interviewer:user_management_add')

    def get_context_data(self, **kwargs):
        context = super(InterviewerSignUpView, self).get_context_data(**kwargs)
        if self.request.user.user_type < 3:
            context['form'].fields['user_type'].choices = [(index, value) for index, value in
                                                           [(index, value) for index, value in
                                                            context['form'].fields['user_type'].choices if
                                                            type(index) == int] if
                                                           (self.request.user.user_type <= index < 10)]
        else:
            context = {}
        return context


@method_decorator([login_required, user_role_less_than_required(role_less_than=10)], name='dispatch')
class InterviewerUpdateView(UpdateView):
    model = User
    template_name = 'interview/interviewer/user_management_edit.html'
    context_object_name = 'consumer'
    form_class = InterviewerUpdateForm

    def get_success_url(self):
        return reverse('interviewer:user_management_edit', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        if self.request.user.user_type == 1:
            company = form.save()
            user = form.save(user_obj=self.request.user)
            messages.success(self.request, 'User was updated successfully')
            return redirect('interviewer:user_management_edit', pk=self.object.pk)
        elif self.request.user.user_type == 2 \
                and "user_type=1" not in str(self.request.body) \
                and Interviewer.objects.filter(user=self.request.user.id).values()[0]['company_id'] == \
                Interviewer.objects.filter(user=User.objects.filter(username=[para for para in
                                                                              self.request.body.decode("utf-8").split(
                                                                                  "&") if para.startswith("email=")][0].replace(
                    "%40", "@").split("=")[-1])[0].id).values()[0]['company_id']:
            user = form.save(user_obj=self.request.user)
            messages.success(self.request, 'User was updated successfully')
            return redirect('interviewer:user_management_edit', pk=self.object.pk)
        messages.error(
            self.request, 'You need permission to perform this action')
        return redirect('interviewer:user_management_edit', pk=self.object.pk)

    def get_context_data(self, **kwargs):
        context = super(InterviewerUpdateView, self).get_context_data(**kwargs)
        if self.request.user.user_type < 3:
            context['form'].fields['user_type'].choices = [(index, value)
                                                           for index, value in [(index, value)
                                                                                for index, value in
                                                                                context['form'].fields['user_type'].choices
                                                                                if type(index) == int]
                                                           if (self.request.user.user_type <= index < 10)]
        else:
            context = {}
        return context

    def get_queryset(self):
        if self.request.user.user_type == 1:
            queryset = User.objects.exclude(user_type=10)
        elif self.request.user.user_type == 2:
            queryset = User.objects.filter(
                working_organization__company__id=Interviewer.objects.filter(user=self.request.user.id).values()[0][
                    'company_id']).exclude(user_type=10)
        else:
            queryset = User.objects.none()
        return queryset


@method_decorator([login_required, user_role_less_than_required(role_less_than=3)], name='dispatch')
class InterviewerDeleteView(DeleteView):
    model = User
    template_name = 'interview/interviewer/user_management_delete.html'
    success_url = reverse_lazy('interviewer:user_management_list')
    context_object_name = "consumer"

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        messages.success(
            request, 'The user %s was deleted with success!' % user.email)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.user_type == 1:
            queryset = User.objects.exclude(user_type=10)
        elif self.request.user.user_type == 2:
            queryset = User.objects.filter(
                working_organization__company__id=Interviewer.objects.filter(user=self.request.user.id).values()[0][
                    'company_id']).exclude(user_type=10)
        else:
            queryset = User.objects.none()
        return queryset


@method_decorator([login_required, user_role_less_than_required(role_less_than=3)], name='dispatch')
class UserManagementListView(ListView):
    model = User
    ordering = ('first_name')
    context_object_name = 'consumers'
    template_name = 'interview/interviewer/user_management_list.html'

    def get_queryset(self):
        if self.request.user.user_type == 1:
            queryset = User.objects.exclude(user_type=10)
        elif self.request.user.user_type == 2:
            queryset = User.objects.filter(
                working_organization__company__id=Interviewer.objects.filter(user=self.request.user.id).values()[0][
                    'company_id']).exclude(user_type=10)
        else:
            queryset = User.objects.none()
        return queryset


@method_decorator([login_required, user_role_less_than_required(role_less_than=3)], name='dispatch')
class CompanyListView(ListView):
    model = Company
    ordering = ('id',)
    context_object_name = 'companies'
    template_name = 'interview/interviewer/company_list.html'


@method_decorator([login_required, user_role_less_than_required(role_less_than=10)], name='dispatch')
class CompanyCreateView(CreateView):
    model = Company
    form_class = CompanyCreateForm
    template_name = 'interview/interviewer/company_create.html'

    def get_success_url(self):
        return reverse('interviewer:company_edit', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        if self.request.user.user_type < 10:
            company = form.save(user_obj=self.request.user)
            messages.success(self.request, 'Company was added successfully')
            return redirect('interviewer:company_list')
        messages.error(
            self.request, 'You need permission to perform this action')
        return redirect('interviewer:company_list')

    def get_context_data(self, **kwargs):
        context = super(CompanyCreateView, self).get_context_data(**kwargs)
        if self.request.user.user_type >= 10:
            context = {}
        return context


@method_decorator([login_required, user_role_less_than_required(role_less_than=10)], name='dispatch')
class CompanyUpdateView(UpdateView):
    model = Company
    template_name = 'interview/interviewer/company_edit.html'
    context_object_name = 'company'
    form_class = CompanyUpdateForm

    def get_success_url(self):
        return reverse('interviewer:company_edit', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        if self.request.user.user_type < 10:
            company = form.save()
            messages.success(
                self.request, 'Company name was edited successfully')
            return redirect('interviewer:company_list')
        messages.error(
            self.request, 'You need permission to perform this action')
        return redirect('interviewer:company_list')

    def get_context_data(self, **kwargs):
        context = super(CompanyUpdateView, self).get_context_data(**kwargs)
        if self.request.user.user_type >= 10:
            context = {}
        return context


@method_decorator([login_required, user_role_less_than_required(role_less_than=10)], name='dispatch')
class CompanyDeleteView(DeleteView):
    model = Company
    template_name = 'interview/interviewer/company_delete.html'
    success_url = reverse_lazy('interviewer:company_list')
    context_object_name = 'company'

    def delete(self, request, *args, **kwargs):
        company = self.get_object()
        messages.success(
            request, 'The company " %s " was deleted with success!' % company.name)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.user_type == 1:
            queryset = Company.objects.filter()
        elif self.request.user.user_type == 2:
            queryset = self.request.user.working_organization.company.owner_company
        elif self.request.user.user_type < 10:
            queryset = self.request.user.company_owner
        else:
            queryset = Company.objects.none()
        return queryset


@method_decorator([login_required, user_role_less_than_required(role_less_than=10)], name='dispatch')
class CompanyEmailView(UpdateView):
    model = Company
    template_name = 'interview/interviewer/company_email.html'
    context_object_name = 'company'
    form_class = CompanyEmailForm

    def get_success_url(self):
        return reverse('interviewer:company_edit', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        if self.request.user.user_type < 10:

            company = form.save()
            messages.success(
                self.request, 'Company Email was edited successfully')
            return redirect('interviewer:company_list')
        messages.error(
            self.request, 'You need permission to perform this action')
        return redirect('interviewer:company_list')

    def get_context_data(self, **kwargs):
        context = super(CompanyEmailView, self).get_context_data(**kwargs)
        if self.request.user.user_type >= 10:
            context = {}
        return context


@method_decorator([login_required, user_role_less_than_required(role_less_than=10)], name='dispatch')
class QuestionCreateView(LoginRequiredMixin, CreateView):
    model = Question
    form_class = QuestionCreateForm
    template_name = 'interview/interviewer/question_create.html'

    def form_valid(self, form):
        if self.request.user.user_type < 10:
            question = form.save(user_obj=self.request.user)
            messages.success(self.request, 'Question was added successfully')
            return redirect('interviewer:questions_list')
        messages.error(
            self.request, 'You need permission to perform this action')
        return redirect('interviewer:questions_list')

    def get_context_data(self, **kwargs):
        context = super(QuestionCreateView, self).get_context_data(**kwargs)
        if self.request.user.user_type >= 10:
            context = {}
        return context


@method_decorator([login_required, user_role_less_than_required(role_less_than=10)], name='dispatch')
class QuestionUpdateView(UpdateView):
    model = Question
    template_name = 'interview/interviewer/question_edit.html'
    context_object_name = 'question'
    form_class = QuestionUpdateForm

    def get_success_url(self):
        return reverse('interviewer:question_edit', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        if self.request.user.user_type < 10:
            question = form.save(user_obj=self.request.user)
            messages.success(self.request, 'Question was edited successfully')
            return redirect('interviewer:questions_list')
        messages.error(
            self.request, 'You need permission to perform this action')
        return redirect('interviewer:questions_list')

    def get_context_data(self, **kwargs):
        context = super(QuestionUpdateView, self).get_context_data(**kwargs)
        if self.request.user.user_type >= 10:
            context = {}
        return context

    def get_queryset(self):
        if self.request.user.user_type == 1:
            queryset = Question.objects.filter()
        elif self.request.user.user_type == 2:
            queryset = self.request.user.working_organization.company.owner_company
        elif self.request.user.user_type < 10:
            queryset = self.request.user.question_owner
        else:
            queryset = Question.objects.none()
        return queryset


@method_decorator([login_required, user_role_less_than_required(role_less_than=10)], name='dispatch')
class QuestionDeleteView(DeleteView):
    model = Question
    template_name = 'interview/interviewer/question_delete.html'
    success_url = reverse_lazy('interviewer:questions_list')
    context_object_name = 'question'

    def delete(self, request, *args, **kwargs):
        question = self.get_object()
        messages.success(
            request, 'The question " %s " was deleted with success!' % question.text)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.user_type == 1:
            queryset = Question.objects.filter()
        elif self.request.user.user_type == 2:
            queryset = self.request.user.working_organization.company.owner_company
        elif self.request.user.user_type < 10:
            queryset = self.request.user.question_owner
        else:
            queryset = Question.objects.none()
        return queryset


@method_decorator([login_required, user_role_less_than_required(role_less_than=10)], name='dispatch')
class QuestionListView(ListView):
    model = Question
    ordering = ('text',)
    context_object_name = 'questions'
    template_name = 'interview/interviewer/question_list.html'

    def get_queryset(self):
        if self.request.user.user_type == 1:
            queryset = Question.objects.filter()
        elif self.request.user.user_type == 2:
            queryset = self.request.user.working_organization.company.owner_company
        elif self.request.user.user_type < 10:
            queryset = self.request.user.question_owner
        else:
            queryset = Question.objects.none()
        return queryset


@method_decorator([login_required, user_role_less_than_required(role_less_than=10)], name='dispatch')
class VacancyListView(ListView):
    model = Vacancy
    ordering = ('position',)
    context_object_name = 'vacancies'
    template_name = 'interview/interviewer/vacancy_list.html'

    def get_queryset(self):
        if self.request.user.user_type == 1:
            queryset = Vacancy.objects.filter()
        elif self.request.user.user_type == 2:
            queryset = self.request.user.working_organization.company.owner_organisation
        elif self.request.user.user_type < 10:
            queryset = self.request.user.vacancy_owner
        else:
            queryset = Vacancy.objects.none()
        return queryset


@method_decorator([login_required, user_role_less_than_required(role_less_than=10)], name='dispatch')
class VacancyCreateView(LoginRequiredMixin, CreateView):
    model = Vacancy
    form_class = VacancyCreateForm
    template_name = 'interview/interviewer/vacancy_create.html'

    def form_valid(self, form):
        if self.request.user.user_type < 10:
            if self.request.POST['start_date'] > self.request.POST['l_date']:
                messages.error(
                    self.request, 'Start date must be less than end date')
                return redirect('interviewer:vacancy_add')
            else:
                vacancy = form.save(user_obj=self.request.user)
                messages.success(
                    self.request, 'Vacancy was added successfully')
                return redirect('interviewer:vacancies_list')
        messages.error(
            self.request, 'You need permission to perform this action')
        return redirect('interviewer:vacancies_list')

    def get_context_data(self, **kwargs):
        context = super(VacancyCreateView, self).get_context_data(**kwargs)
        if self.request.user.user_type < 10:
            context['form'].fields['status'].choices = [(index, value) for index, value in
                                                        context['form'].fields['status'].choices if
                                                        index != ""]
        else:
            context = {}
        return context


@method_decorator([login_required, user_role_less_than_required(role_less_than=10)], name='dispatch')
class VacancyUpdateView(UpdateView):
    model = Vacancy
    template_name = 'interview/interviewer/vacancy_edit.html'
    context_object_name = 'vacancy'
    form_class = VacancyUpdateForm

    def get_success_url(self):
        return reverse('interviewer:vacancy_edit', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        if self.request.user.user_type < 10:
            if self.request.POST['start_date'] > self.request.POST['end_date']:
                messages.error(
                    self.request, 'Start date must be less than end date')
                return redirect('interviewer:vacancy_add')
            else:
                vacancy = form.save(user_obj=self.request.user)
                messages.success(
                    self.request, 'Vacancy was edited successfully')
                return redirect('interviewer:vacancies_list')
        messages.error(
            self.request, 'You need permission to perform this action')
        return redirect('interviewer:vacancies_list')

    def get_context_data(self, **kwargs):
        context = super(VacancyUpdateView, self).get_context_data(**kwargs)
        if self.request.user.user_type < 10:
            context['form'].fields['status'].choices = [(index, value) for index, value in
                                                        context['form'].fields['status'].choices if
                                                        index != ""]
        else:
            context = {}
        return context

    def get_queryset(self):
        if self.request.user.user_type == 1:
            queryset = Vacancy.objects.filter()
        elif self.request.user.user_type == 2:
            queryset = self.request.user.working_organization.company.owner_organisation
        elif self.request.user.user_type < 10:
            queryset = self.request.user.vacancy_owner
        else:
            queryset = Vacancy.objects.none()
        return queryset


@method_decorator([login_required, user_role_less_than_required(role_less_than=10)], name='dispatch')
class VacancyDeleteView(DeleteView):
    model = Vacancy
    template_name = 'interview/interviewer/vacancy_delete.html'
    success_url = reverse_lazy('interviewer:vacancies_list')
    context_object_name = 'vacancy'

    def delete(self, request, *args, **kwargs):
        vacancy = self.get_object()
        messages.success(
            request, 'The vacancy " %s " was deleted with success!' % vacancy.position)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.user_type == 1:
            queryset = Vacancy.objects.filter()
        elif self.request.user.user_type == 2:
            queryset = self.request.user.working_organization.company.owner_organisation
        elif self.request.user.user_type < 10:
            queryset = self.request.user.vacancy_owner
        else:
            queryset = Vacancy.objects.none()
        return queryset


@method_decorator([login_required, user_role_less_than_required(role_less_than=10)], name='dispatch')
class InterviewListView(ListView):
    model = Interview
    ordering = ('position_name',)
    context_object_name = 'interviews'
    template_name = 'interview/interviewer/interview_list.html'

    def get_queryset(self):
        if self.request.user.user_type == 1:
            queryset = Interview.objects.filter().annotate(Count('taken_interviews'))
        elif self.request.user.user_type == 2:
            queryset = self.request.user.working_organization.company.interview_organisation.annotate(
                Count('taken_interviews'))
        elif self.request.user.user_type < 10:
            queryset = self.request.user.working_organization.interview_owner.annotate(
                Count('taken_interviews'))
        else:
            queryset = Interview.objects.none()
        return queryset

    def get_context_data(self, **kwargs):
        context = super(InterviewListView, self).get_context_data(**kwargs)
        new_list = []
        for interview in context['interviews']:
            interview.completed_count = interview.taken_interviews.filter(
                status=3).count()
            new_list.append(interview)
        context['interviews'] = new_list
        return context


@method_decorator([login_required, user_role_less_than_required(role_less_than=10)], name='dispatch')
class InterviewCreateView(LoginRequiredMixin, CreateView):
    model = Interview
    form_class = InterviewCreateForm
    template_name = 'interview/interviewer/interview_create.html'
    context_object_name = "interview"

    def form_valid(self, form):
        if self.request.user.user_type < 10:
            if 'questions' not in self.request.POST:
                messages.error(
                    self.request, 'Questions should not be empty list')
                return redirect('interviewer:interview_add')
            elif 'position_name' not in self.request.POST:
                messages.error(
                    self.request, 'Position Name should be valid selection')
                return redirect('interviewer:interview_add')
            else:
                interview = form.save(user_obj=self.request.user)
                messages.success(
                    self.request, 'Interview was added successfully')
                return redirect('interviewer:interview_candidates_list', pk=interview.pk)
        messages.error(
            self.request, 'You need permission to perform this action')
        return redirect('interviewer:interviews_list')

    def get_context_data(self, **kwargs):
        context = super(InterviewCreateView, self).get_context_data(**kwargs)
        if self.request.user.user_type == 1:
            context['question_list'] = Question.objects.filter()
        elif self.request.user.user_type == 2:
            context['question_list'] = Question.objects.filter(
                owner_company=self.request.user.working_organization.company)
            context['form'].fields[
                'position_name'].queryset = self.request.user.vacancy_owner.filter(status='Active')
        elif self.request.user.user_type < 10:
            context['question_list'] = Question.objects.filter(
                question_owner=self.request.user)
            context['form'].fields['position_name'].queryset = self.request.user.vacancy_owner.filter(
                status='Active')
        else:
            context = {}
        return context


@method_decorator([login_required, user_role_less_than_required(role_less_than=10)], name='dispatch')
class InterviewUpdateView(UpdateView):
    model = Interview
    template_name = 'interview/interviewer/interview_edit.html'
    context_object_name = 'interview'
    form_class = InterviewUpdateForm

    def get_success_url(self):
        return reverse('interviewer:interview_edit', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        if self.request.user.user_type < 10:
            if 'questions' not in self.request.POST:
                messages.error(
                    self.request, 'Questions should not be empty list')
                return redirect('interviewer:interview_add')
            elif 'position_name' not in self.request.POST:
                messages.error(
                    self.request, 'Position Name should be valid selection')
                return redirect('interviewer:interview_add')
            else:
                interview = form.save(user_obj=self.request.user)
                messages.success(
                    self.request, 'Interview was edited successfully')
                return redirect('interviewer:interviewee_add', pk=self.object.pk)
        messages.error(
            self.request, 'You need permission to perform this action')
        return redirect('interviewer:interviews_list')

    def get_context_data(self, **kwargs):
        context = super(InterviewUpdateView, self).get_context_data(**kwargs)
        qu_json = dict()
        for index, qu in enumerate(Interview.objects.filter(id=context['object'].id)[0].questions.all()):
            qu_json[str(index+1)] = {'time': int(qu.time),
                                     'question': str(qu.text)}
        context['form'].fields['question_s'].widget.attrs['value'] = json.dumps(
            qu_json)
        if self.request.user.user_type == 1:
            context['question_list'] = Question.objects.filter()
        elif self.request.user.user_type == 2:
            context['question_list'] = Question.objects.filter(
                owner_company=self.request.user.working_organization.company)
            context['form'].fields[
                'position_name'].queryset = self.request.user.vacancy_owner
        elif self.request.user.user_type < 10:
            context['question_list'] = Question.objects.filter(
                question_owner=self.request.user)
            context['form'].fields['position_name'].queryset = self.request.user.vacancy_owner
        else:
            context = {}
        return context

    def get_queryset(self):
        if self.request.user.user_type == 1:
            queryset = Interview.objects.filter()
        elif self.request.user.user_type == 2:
            queryset = self.request.user.working_organization.company.interview_organisation
        elif self.request.user.user_type < 10:
            queryset = self.request.user.working_organization.interview_owner
        else:
            queryset = Interview.objects.none()
        return queryset


@method_decorator([login_required, user_role_less_than_required(role_less_than=10)], name='dispatch')
class InterviewDeleteView(DeleteView):
    model = Interview
    template_name = 'interview/interviewer/interview_delete.html'
    success_url = reverse_lazy('interviewer:interviews_list')
    context_object_name = 'interview'

    def delete(self, request, *args, **kwargs):
        interview = self.get_object()
        messages.success(request, 'The interview " %s " was deleted with success!' %
                         interview.position_name.position)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.user_type == 1:
            queryset = Interview.objects.filter()
        elif self.request.user.user_type == 2:
            queryset = self.request.user.working_organization.company.interview_organisation
        elif self.request.user.user_type < 10:
            queryset = self.request.user.working_organization.interview_owner
        else:
            queryset = Interview.objects.none()
        return queryset


@login_required
@user_role_less_than_required(role_less_than=10)
def interviewee_create(request, *args, **kwrgs):

    if request.user.user_type == 1:
        interview = get_object_or_404(Interview, pk=kwrgs['pk'])
    elif request.user.user_type == 2:
        interview = get_object_or_404(Interview, pk=kwrgs['pk'],
                                      interview_organisation=request.user.working_organization.company)
    else:
        interview = get_object_or_404(
            Interview, pk=kwrgs['pk'], interview_owner=request.user.working_organization)

    if request.method == 'POST':
        form = IntervieweeSignUpForm(request.POST)
        if form.is_valid():
            if TakenInterview.objects.filter(candidate__user_for_interview__username=form.cleaned_data['email'],
                                             taken_interviews=interview, status=1).count() == 0 and \
                    TakenInterview.objects.filter(candidate__user_for_interview__username=form.cleaned_data['email'],
                                                  taken_interviews=interview, status=2).count() == 0:
                with transaction.atomic():

                    if len(User.objects.filter(username=form.cleaned_data['email'])) == 0:
                        password = User.objects.make_random_password(length=10)
                        print(password)
                        user = User.objects.create_user(form.cleaned_data['email'], form.cleaned_data['email'], password,
                                                        user_type=10)
                        user.save()
                    else:
                        user = User.objects.filter(
                            username=form.cleaned_data['email'])[0]
                        user.is_active = True
                        password = User.objects.make_random_password(length=10)
                        user.set_password(password)
                        user.save()
                    interviewee = form.save(commit=False)
                    user.first_name = interviewee.name
                    interviewee.user_for_interview = user
                    user.save()
                    interviewee.save()

                ti = TakenInterview.objects.create(taken_interviews=interview,
                                                   candidate=interviewee,
                                                   status=1,
                                                   )
                for q in interview.question_interview.filter().order_by('index'):
                    answer = ti.answers.add(Answer.objects.create(
                        candidate=interviewee,
                        question=q.question,
                        text="",
                        index=q.index
                    )
                    )

                subject = 'Interview Invitation'
                email_template = interview.interview_organisation.email_template
                print(email_template)

                if(len(email_template) == 0):
                    message = 'Dear ' + interviewee.name + ",\n\n" + \
                        "<p>Congratulations we would like to invite you to next stage of our recruitment process which will be completing an interview online.</p>" + \
                              "<p>As part of the video interview, you will be required to answer a series of questions related to our company and the position.</p>" + \
                              "<p>The interview can be conducted on either your desktop, tablet or mobile phone.</p>" + \
                              "<p>For each question, you will be asked to record your answer within the stated timeframe and then upload the recording from the privacy of your own home or anywhere you feel comfortable.</p>" + \
                              "<p><strong>Remember this is an interview and we will be reviewing your answers and how you present yourself.</strong></p> " + \
                              "<p>Your username and password are shown below,</p>" +\
                              "<p>Username: " + form.cleaned_data['email'] + "<br>" + \
                              "Password: " + str(password) + "</p>" + \
                              "<p>Please click on below link to start your interview<br>" + \
                              "<a href='https://www.viddi.com.au' target='_blank'>https://www.viddi.com.au</a></p>" + \
                              "<p><i>The opportunity to complete your video interview will expire typically in 72 hours from receipt of this email.</i></p>" + \
                              "<p>If you are successful, we will be in contact shortly to coordinate next steps.</p>" + \
                              "<p>At any stage of the process you if have any questions please do not hesitate to let us know by emailing <a href='mailto:craig@goturbo.com.au'>craig@goturbo.com.au</a></p>" + \
                              "<p>All the best for your interview!</p>" + \
                              "<p>The " + \
                        str(interview.interview_organisation.name) + " team.</p>"
                else:
                    message = email_template.replace(
                        '{{interviewer.name}}', interviewee.name).replace(
                        '{{interviewer.email}}', form.cleaned_data['email']).replace(
                        '{{interviewer.password}}', str(password)).replace(
                        '{{organisation.name}}', str(interview.interview_organisation.name))

                # if str(interview.interview_organisation.name) == 'Hostplus':
                #     message = 'Dear ' + interviewee.name + ",\n\n" + \
                #               "<p>Congratulations we would like to invite you to next stage of our recruitment process which will be completing an interview online.</p>" + \
                #               "<p>As part of the video interview, you will be required to answer a series of questions related to our company and the position.</p>" + \
                #               "<p>The interview can be conducted on either your desktop, tablet or mobile phone.</p>" + \
                #               "<p>For each question, you will be asked to record your answer within the stated timeframe and then upload the recording from the privacy of your own home or anywhere you feel comfortable.</p>" + \
                #               "<p><strong>Remember this is an interview and we will be reviewing your answers and how you present yourself.</strong></p> " + \
                #               "<p>Your username and password are shown below,</p>" +\
                #               "<p>Username: " + form.cleaned_data['email'] + "<br>" + \
                #               "Password: " + str(password) + "</p>" + \
                #               "<p>Please click on below link to start your interview<br>" + \
                #               "<a href='https://www.viddi.com.au' target='_blank'>https://www.viddi.com.au</a></p>" + \
                #               "<p><i>The opportunity to complete your video interview will expire typically in 72 hours from receipt of this email.</i></p>" + \
                #               "<p>If you are successful, we will be in contact shortly to coordinate next steps.</p>" + \
                #               "<p>At any stage of the process you if have any questions please do not hesitate to let us know by emailing <a href='mailto:cscrecruitment@hostplus.com.au'>cscrecruitment@hostplus.com.au</a></p>" + \
                #               "<p>All the best for your interview!</p>" + \
                #               "<p>The " + \
                #         str(interview.interview_organisation.name) + " team.</p>"
                # elif str(interview.interview_organisation.name) == 'Logan City Council':
                #     message = 'Dear ' + interviewee.name + ",\n\n" + \
                #               "<p>Congratulations we would like to invite you to next stage of our recruitment process which will be completing an interview online.</p>" + \
                #               "<p>As part of the video interview, you will be required to answer a series of questions related to our company and the position.</p>" + \
                #               "<p>The interview can be conducted on either your desktop, tablet or mobile phone.</p>" + \
                #               "<p>For each question, you will be asked to record your answer within the stated timeframe and then upload the recording from the privacy of your own home or anywhere you feel comfortable.</p>" + \
                #               "<p><strong>Remember this is an interview and we will be reviewing your answers and how you present yourself.</strong></p> " + \
                #               "<p>Your username and password are shown below,</p>" +\
                #               "<p>Username: " + form.cleaned_data['email'] + "<br>" + \
                #               "Password: " + str(password) + "</p>" + \
                #               "<p>Please click on below link to start your interview<br>" + \
                #               "<a href='https://www.viddi.com.au' target='_blank'>https://www.viddi.com.au</a></p>" + \
                #               "<p><i>The opportunity to complete your video interview will expire typically in 72 hours from receipt of this email.</i></p>" + \
                #               "<p>If you are successful, we will be in contact shortly to coordinate next steps.</p>" + \
                #               "<p>At any stage of the process you if have any questions please do not hesitate to let us know by emailing <a href='mailto:craig@goturbo.com.au'>craig@goturbo.com.au</a></p>" + \
                #               "<p>All the best for your interview!</p>" + \
                #               "<p>The " + \
                #         str(interview.interview_organisation.name) + " team.</p>"
                # else:
                #     message = 'Dear ' + interviewee.name + ",\n\n" + \
                #         "<p>Congratulations we would like to invite you to next stage of our recruitment process which will be completing an interview online.</p>" + \
                #               "<p>As part of the video interview, you will be required to answer a series of questions related to our company and the position.</p>" + \
                #               "<p>The interview can be conducted on either your desktop, tablet or mobile phone.</p>" + \
                #               "<p>For each question, you will be asked to record your answer within the stated timeframe and then upload the recording from the privacy of your own home or anywhere you feel comfortable.</p>" + \
                #               "<p><strong>Remember this is an interview and we will be reviewing your answers and how you present yourself.</strong></p> " + \
                #               "<p>Your username and password are shown below,</p>" +\
                #               "<p>Username: " + form.cleaned_data['email'] + "<br>" + \
                #               "Password: " + str(password) + "</p>" + \
                #               "<p>Please click on below link to start your interview<br>" + \
                #               "<a href='https://www.viddi.com.au' target='_blank'>https://www.viddi.com.au</a></p>" + \
                #               "<p><i>The opportunity to complete your video interview will expire typically in 72 hours from receipt of this email.</i></p>" + \
                #               "<p>If you are successful, we will be in contact shortly to coordinate next steps.</p>" + \
                #               "<p>At any stage of the process you if have any questions please do not hesitate to let us know by emailing <a href='mailto:craig@goturbo.com.au'>craig@goturbo.com.au</a></p>" + \
                #               "<p>All the best for your interview!</p>" + \
                #               "<p>The " + \
                #         str(interview.interview_organisation.name) + " team.</p>"

                email_from = settings.EMAIL_HOST_USERNAME
                # recipient_list = [str(form.cleaned_data['email']), ]
                to = str(form.cleaned_data['email'])
                msg = EmailMultiAlternatives(subject, '', email_from, [to])
                msg.attach_alternative(message, "text/html")
                msg.send()
                # send_mail(subject, message, email_from, recipient_list, html_message='text/html')

                messages.success(
                    request, 'Candidate is invited for an interview.')
                return redirect('interviewer:interview_candidates_list', pk=interview.pk)

            else:
                messages.warning(
                    request, 'Interview is already scheduled for this Candidate.')
                return redirect('interviewer:interview_candidates_list', pk=interview.pk)

    else:
        form = IntervieweeSignUpForm()

    return render(request, 'interview/interviewer/interviewee_create.html', {'interview_id': kwrgs['pk'], 'form': form})


@login_required
@user_role_less_than_required(role_less_than=10)
def interviewee_review(request, *args, **kwrgs):
    if request.user.user_type == 1:
        interview_instance = get_object_or_404(Interview, pk=kwrgs['interview_pk']).taken_interviews.filter(
            candidate__pk=kwrgs['candidate_pk'])
    elif request.user.user_type == 2:
        interview_instance = \
            get_object_or_404(Interview,
                              pk=kwrgs['interview_pk'],
                              interview_organisation=request.user.working_organization.company).taken_interviews.filter(
                candidate__pk=kwrgs['candidate_pk'])
    else:
        interview_instance = \
            get_object_or_404(Interview,
                              pk=kwrgs['interview_pk'],
                              interview_owner=request.user.working_organization).taken_interviews.filter(
                candidate__pk=kwrgs['candidate_pk'])

    # Check if detail shared with this user.
    if len(interview_instance) == 0:
        # Work pending : Testing require to check filter for shared to user
        interview_instance = get_object_or_404(Interview, pk=kwrgs['interview_pk']).taken_interviews.filter(
            candidate__pk=kwrgs['candidate_pk']).filter(shared_to_users=request.user.working_organization)

    # Find latest instance of interview created
    if len(interview_instance) == 1:
        interview_instance = interview_instance[0]
    elif len(interview_instance) > 1:
        interview_instance = interview_instance.order_by(
            '-interview_create_date')[0]

    if request.user.user_type == 1:
        interviewer_object = Interviewer.objects.filter().exclude(
            user__username=request.user.username)
    else:
        interviewer_object = request.user.working_organization.company.working_organization.exclude(
            user__username=request.user.username)

    if request.method == 'POST':
        if isinstance(interview_instance, TakenInterview):
            if 'review' in request.POST:
                if ('ratingStatus' in request.POST) and ('rating' in request.POST) and (
                        'comment' in request.POST):
                    if int(request.POST['ratingStatus']) not in [key for key, value in
                                                                 Review.REVIEW_STATUS_TYPE_CHOICES]:
                        messages.error(
                            request, 'Invalid Parameter: "Rating Status"')
                    elif int(request.POST['rating']) not in [key for key, value in
                                                             Review.ONE_TO_FIVE_RATING_CHOICES]:
                        messages.error(request, 'Invalid Parameter "Rating"')
                    elif int(len(request.POST['comment'])) > 255:
                        messages.error(
                            request, 'Length of comment cannot be greater than 255')
                    else:
                        interview_instance.review.add(Review.objects.create(
                            reviewer=request.user.working_organization,
                            review_status=int(request.POST['ratingStatus']),
                            rating=int(request.POST['rating']),
                            comment=str(request.POST['comment'])))
                        messages.success(
                            request, "Review created successfully")
                else:
                    messages.error(request,
                                   'Invalid Review parameters: Required "Rating Status", "Rating" and '
                                   '"Comment" is required')
            elif 'share' in request.POST:
                if 'shareToUsers' in request.POST:
                    if len(interviewer_object.filter(user__username=request.POST['shareToUsers'])) == 0:
                        messages.error(
                            request, 'Invalid Parameter: "User Detail"')
                    else:
                        interviewer_instance = interviewer_object.filter(
                            user__username=request.POST['shareToUsers'])[0]
                        interview_instance.shared_to_users.add(
                            interviewer_instance)
                        messages.success(
                            request, "Candidate details shared successfully")

                        subject = 'Interview Invitation'
                        message = 'Dear ' + interviewer_instance.user.first_name + ",\n\n" + str(
                            request.user.first_name) + str(
                            request.user.last_name) + "has shared below candidate details" + str(
                            request.get_full_path()) + "\n\n" + "Thank you," + "\n" + str(
                            request.user.working_organization.company.name)

                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = [
                            str(interviewer_instance.user.email), ]
                        send_mail(subject, message, email_from, recipient_list)
                else:
                    messages.error(request, 'Invalid Share parameters')
        else:
            messages.error(
                request, "You need permission to perform this action")

    form = IntervieweeSignUpForm(instance=interview_instance)

    if len(interview_instance.review.filter()) > 0:
        reviews = interview_instance.review.order_by(
            '-review_create_date')
        last_review = reviews.reverse()[0]
    else:
        reviews = []
        last_review = ""

    return render(request, 'interview/interviewer/interviewee_review.html',
                  {'interview_id': kwrgs['interview_pk'], 'candidate_id': kwrgs['candidate_pk'],
                   'interview_instance': interview_instance, 'interviewer_object': interviewer_object,
                   'form': form, 'reviews': reviews,
                   'last_review': last_review})


@method_decorator([login_required, user_role_less_than_required(role_less_than=10)], name='dispatch')
class InterviewCandidateListView(ListView):
    model = Interview
    context_object_name = 'interviews'
    template_name = 'interview/interviewer/interview_candidate_list.html'

    def get_queryset(self):
        if self.request.user.user_type == 1:
            # Work pending - Need to filter candidates by interview
            queryset = Interview.objects.filter(id=self.kwargs['pk'])
        elif self.request.user.user_type == 2:
            queryset = self.request.user.working_organization.company.interview_organisation.filter(
                id=self.kwargs['pk'])
        elif self.request.user.user_type < 10:
            queryset = self.request.user.working_organization.interview_owner.filter(
                id=self.kwargs['pk'])
        else:
            queryset = Interview.objects.none()
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(InterviewCandidateListView,
                        self).get_context_data(**kwargs)
        context['interview_pk'] = self.kwargs['pk']
        for interview in context['interviews']:
            taken_interviews = interview.taken_interviews.select_related('candidate__user_for_interview').order_by(
                '-interview_create_date')
            total_taken_interviews = taken_interviews.count()
            context['taken_interviews'] = taken_interviews
            context['total_taken_interviews'] = total_taken_interviews
        return context


@method_decorator([login_required, user_role_less_than_required(role_less_than=10)], name='dispatch')
class InterviewCompleteCandidateListView(ListView):
    model = Interview
    context_object_name = 'interviews'
    template_name = 'interview/interviewer/interview_candidate_list.html'

    def get_queryset(self):
        if self.request.user.user_type == 1:
            # Work pending - Need to filter candidates by interview
            queryset = Interview.objects.filter(id=self.kwargs['pk'])
        elif self.request.user.user_type == 2:
            queryset = self.request.user.working_organization.company.interview_organisation.filter(
                id=self.kwargs['pk'])
        elif self.request.user.user_type < 10:
            queryset = self.request.user.working_organization.interview_owner.filter(
                id=self.kwargs['pk'])
        else:
            queryset = Interview.objects.none()
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super(InterviewCompleteCandidateListView,
                        self).get_context_data(**kwargs)
        context['interview_pk'] = self.kwargs['pk']
        for interview in context['interviews']:
            taken_interviews = \
                interview.taken_interviews.filter(status=3).select_related('candidate__user_for_interview').order_by(
                    '-interview_create_date')
            total_taken_interviews = taken_interviews.count()
            context['taken_interviews'] = taken_interviews
            context['total_taken_interviews'] = total_taken_interviews
        return context


@method_decorator([login_required, user_role_less_than_required(role_less_than=10)], name='dispatch')
class CandidateListView(ListView):
    model = TakenInterview
    context_object_name = 'taken_interviews'
    template_name = 'interview/interviewer/candidate_list.html'

    def get_queryset(self):
        if self.request.user.user_type == 1:
            queryset = TakenInterview.objects.filter()
        elif self.request.user.user_type == 2:
            queryset = TakenInterview.objects.filter(
                taken_interviews__interview_organisation=self.request.user.working_organization.company)
        elif self.request.user.user_type < 10:
            queryset = TakenInterview.objects.filter(
                taken_interviews__interview_owner=self.request.user.working_organization)
        else:
            queryset = TakenInterview.objects.none()
        queryset.union(TakenInterview.objects.filter(
            shared_to_users__user=self.request.user))
        return queryset


@method_decorator([login_required, user_role_less_than_required(role_less_than=10)], name='dispatch')
class CandidateDeleteView(DeleteView):
    model = TakenInterview
    template_name = 'interview/interviewer/candidate_delete.html'
    success_url = reverse_lazy('interviewer:candidates_list')
    context_object_name = 'interview_taken'

    def delete(self, request, *args, **kwargs):
        interview_taken = self.get_object()
        if interview_taken.candidate.interviews.count() < 2:
            interview_taken.candidate.user_for_interview.is_active = False
        messages.success(request, 'The candidate " %s " was deleted with success!' %
                         interview_taken.candidate.name)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.user_type == 1:
            queryset = TakenInterview.objects.filter()
        elif self.request.user.user_type == 2:
            queryset = TakenInterview.objects.filter(
                taken_interviews__interview_organisation=self.request.user.working_organization.company)
        elif self.request.user.user_type < 10:
            queryset = TakenInterview.objects.filter(
                taken_interviews__interview_owner=self.request.user.working_organization)
        else:
            queryset = TakenInterview.objects.none()
        return queryset


@login_required
@user_role_less_than_required(role_less_than=2)
def manage_settings(request, *args, **kwrgs):

    if request.method == 'POST':
        if 'welcomeMessage' in request.POST and 'instructions' in request.POST and 'completionMessage' in request.POST \
                and 'PracticeInterview' in request.POST:
            if len(Interview.objects.filter(id=request.POST['PracticeInterview'])) > 0:
                Settings.objects.filter(organisation=request.user.working_organization.company).update(
                    welcome_message=request.POST['welcomeMessage'],
                    interview_instructions=request.POST['instructions'],
                    thank_you_message=request.POST['completionMessage'],
                    practice_interview=Interview.objects.filter(
                        id=request.POST['PracticeInterview'])[0]
                )
            else:
                messages.error(request, 'Invalid Selection')
    else:
        pass

    interview_list = []
    if Settings.objects.filter(organisation=request.user.working_organization.company).count() == 0:
        s = Settings.objects.create(
            setting_updated_by=request.user.working_organization,
            organisation=request.user.working_organization.company
        )[0]
    else:
        s = Settings.objects.filter(
            organisation=request.user.working_organization.company
        )[0]
    interview_list = [(0, "")] + [(n.id, n.position_name.position) for n in Interview.objects.all()]\
        if s.practice_interview is None \
        else [(s.practice_interview.id, s.practice_interview.position_name)] + \
             [(n.id, n.position_name.position)
              for n in Interview.objects.all() if n.id != s.practice_interview.id]
    if len(interview_list) == 0:
        interview_list = [(0, "")]
    selected_index = interview_list[0][0]
    return render(request, 'interview/interviewer/settings.html', {'settings': s, 'interview_list': interview_list,
                                                                   'selected_index': selected_index})


@login_required
@user_role_less_than_required(role_less_than=10)
def manage_dashboard(request, *args, **kwrgs):
    if request.user.user_type == 1:
        vacancies_count = Vacancy.objects.count()
        interview_count = Interview.objects.count()
        candidate_count = TakenInterview.objects.count()
        question_count = Question.objects.count()
    elif request.user.user_type == 2:
        vacancies_count = request.user.working_organization.company.owner_organisation.count()
        interview_count = request.user.working_organization.company.interview_organisation.count()
        candidate_count = TakenInterview.objects.filter(
            taken_interviews__interview_organisation=request.user.working_organization.company).count()
        question_count = request.user.working_organization.company.owner_company.count()
    elif request.user.user_type < 10:
        vacancies_count = request.user.vacancy_owner.count()
        interview_count = request.user.working_organization.interview_owner.count()
        candidate_count = TakenInterview.objects.filter(
            taken_interviews__interview_owner=request.user.working_organization).count()
        question_count = request.user.question_owner.count()
    else:
        vacancies_count = Vacancy.objects.none()
        interview_count = Interview.objects.none()
        candidate_count = TakenInterview.objects.none()
        question_count = Question.objects.none()

    return render(request, 'interview/interviewer/dashboard.html', {'vacancies_count': vacancies_count,
                                                                    'interview_count': interview_count,
                                                                    'candidate_count': candidate_count,
                                                                    'question_count': question_count})


# Query Samples
# https://docs.djangoproject.com/en/2.2/ref/models/querysets/#django.db.models.query.QuerySet
# queryset = User.objects.filter(working_organization__company__id=1)
# Interviewer.objects.filter(user=self.request.user.id).values()
# len(Interviewer.objects.filter().values())
# Interviewer.objects.filter(user_id=2).values()
# Interviewer.objects.filter(user_id=2).update(company=2)
# queryset.union(TakenInterview.objects.filter(shared_to_users__user=self.request.user))
