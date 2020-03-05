from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.html import escape, mark_safe
import datetime
from django import forms


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        (1, 'Super Admin'),
        (2, 'Company Admin'),
        (3, 'Company Reviewer'),
        (10, 'Student'),
    )
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES)
    company_name = models.CharField(max_length=100, default="")

    def __str__(self):
        return self.email

    def get_html_badge(self):
        company_name = escape(self.company_name)
        html = '<span class="badge badge-primary" style="background-color: %s">%s</span>' % (
            company_name)
        return mark_safe(html)

class Company(models.Model):
    name = models.CharField('Company', max_length=30)
    img = models.ImageField(upload_to='')
    about = models.TextField('About', blank=True)
    email = models.CharField(max_length=100, null=True)
    email_template = models.TextField('Email Template', blank=True)
    address = models.TextField('Address', blank=True)
    color = models.CharField(max_length=7, default='#007bff')

    def __str__(self):
        return self.name

    def get_html_badge(self):
        name = escape(self.name)
        color = escape(self.color)
        html = '<span class="badge badge-primary" style="background-color: %s">%s</span>' % (
            color, name)
        return mark_safe(html)


class Interviewer(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, related_name='working_organization')
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='working_organization')

    def __str__(self):
        return self.user.username


class Question(models.Model):
    question_owner = models.ForeignKey(
        User, on_delete=models.SET(1), related_name='question_owner')
    text = models.CharField('Question', max_length=255)
    time = models.PositiveIntegerField('Time', default=30)
    owner_company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='owner_company')

    def __str__(self):
        return self.text


class Vacancy(models.Model):

    STATUS_TYPE_CHOICES = (
        ('Active', 'Active'),
        ('Pause', 'Pause'),
    )

    vacancy_owner = models.ForeignKey(
        User, on_delete=models.SET(1), related_name='vacancy_owner')
    position = models.CharField('Position', max_length=255)
    description = models.TextField(blank=True, default='')
    count = models.PositiveIntegerField('Vacancy Count', default=1)
    status = models.CharField(choices=STATUS_TYPE_CHOICES, max_length=10)
    # status = models.PositiveSmallIntegerField(choices=STATUS_TYPE_CHOICES)
    start_date = models.DateField(
        default=datetime.date.today().strftime("%d/%m/%Y"))
    end_date = models.DateField(
        default=datetime.date.today().strftime("%d/%m/%Y"))
    organisation = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='owner_organisation')

    def __str__(self):
        return self.position


class Interview(models.Model):
    interview_owner = models.ForeignKey(
        Interviewer, on_delete=models.SET(1), related_name='interview_owner')
    position_name = models.OneToOneField(
        Vacancy, on_delete=models.CASCADE, related_name='position_name')
    interview_organisation = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='interview_organisation')
    # questions = models.ManyToManyField(Question, related_name='questions')
    questions = models.ManyToManyField(Question, through='InterviewQuestions')

    def __str__(self):
        return self.position_name.position


class InterviewQuestions(models.Model):
    taken_interviews = models.ForeignKey(
        Interview, on_delete=models.CASCADE, related_name='question_interview')
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='question_link')
    index = models.PositiveIntegerField('Question Index', default=1)


class Interviewee(models.Model):
    user_for_interview = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True,
                                              related_name='user_for_interview')
    interviews = models.ManyToManyField(Interview, through='TakenInterview')
    phone = models.CharField(max_length=30, blank=True)
    name = models.CharField(max_length=30, default="", blank=True)

    def __str__(self):
        return self.user_for_interview.username


class Review(models.Model):
    REVIEW_STATUS_TYPE_CHOICES = (
        (0, 'Not reviewed'),
        (1, 'Shortlisted'),
        (2, 'Rejected'),
    )
    ONE_TO_FIVE_RATING_CHOICES = (
        (0, '0'),
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    )
    reviewer = models.ForeignKey(
        Interviewer, on_delete=models.SET(1), related_name='reviewer_owner')
    review_status = models.PositiveSmallIntegerField(
        choices=REVIEW_STATUS_TYPE_CHOICES, default=0)
    rating = models.PositiveSmallIntegerField(
        choices=ONE_TO_FIVE_RATING_CHOICES, default=0)
    comment = models.CharField(max_length=255)
    review_create_date = models.DateTimeField(auto_now_add=True)


class Answer(models.Model):
    candidate = models.ForeignKey(
        Interviewee, on_delete=models.CASCADE, related_name='candidate_answer')
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='candidate_question')
    video_id = models.CharField(max_length=255, default='')
    video_name = models.CharField(max_length=1024, default='')
    location = models.CharField(max_length=1024, default='')
    text = models.CharField('Answer', max_length=255, default='')
    index = models.PositiveIntegerField('Question Index', default=1)

    def __str__(self):
        return self.text


class TakenInterview(models.Model):
    INTERVIEW_STATUS_TYPE_CHOICES = (
        (1, 'Pending'),
        (2, 'Active'),
        (3, 'Complete'),
        (4, 'Canceled'),
        (5, 'Expired'),
        (101, 'Practice Pending'),
        (102, 'Practice Active'),
        (103, 'Practice Complete'),
    )

    taken_interviews = models.ForeignKey(
        Interview, on_delete=models.CASCADE, related_name='taken_interviews')
    candidate = models.ForeignKey(
        Interviewee, on_delete=models.CASCADE, related_name='candidate')
    status = models.PositiveSmallIntegerField(
        choices=INTERVIEW_STATUS_TYPE_CHOICES)
    review = models.ManyToManyField(Review, related_name='review')
    answers = models.ManyToManyField(Answer, related_name='answer')
    interview_create_date = models.DateTimeField(auto_now_add=True)
    interview_attempt_date = models.DateTimeField(blank=True, null=True)
    shared_to_users = models.ManyToManyField(
        Interviewer, related_name='shared_to_users')


class PracticeInterview(models.Model):
    INTERVIEW_STATUS_TYPE_CHOICES = (
        (101, 'Practice Pending'),
        (102, 'Practice Active'),
        (103, 'Practice Complete'),
    )

    taken_interviews = models.ForeignKey(
        Interview, on_delete=models.CASCADE, related_name='practice_interviews')
    candidate = models.ForeignKey(
        Interviewee, on_delete=models.CASCADE, related_name='practice_candidate')
    status = models.PositiveSmallIntegerField(
        choices=INTERVIEW_STATUS_TYPE_CHOICES)
    answers = models.ManyToManyField(Answer, related_name='practice_answer')
    interview_create_date = models.DateTimeField(auto_now_add=True)
    interview_attempt_date = models.DateTimeField(blank=True, null=True)


class Settings(models.Model):
    VIDEO_TYPE_CHOICES = (
        (1, 'Add Pipe'),
    )
    setting_updated_by = models.ForeignKey(
        Interviewer, on_delete=models.SET(1), related_name='setting_updated_by')
    setting_updated_date = models.DateTimeField(auto_now_add=True)
    organisation = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='setting_organisation')
    welcome_message = models.TextField(
        blank=True, default='Welcome to Video Interview')
    interview_instructions = models.TextField(
        blank=True, default='Please complete questions within the time Limit.')
    thank_you_message = models.TextField(blank=True,
                                         default='Thank you for completing to video interview process. '
                                                 'We will be in touch shortly.')
    status = models.PositiveSmallIntegerField(
        choices=VIDEO_TYPE_CHOICES, default=1)
    practice_interview = models.ForeignKey(Interview, null=True, on_delete=models.SET(1),
                                           related_name='setting_practice_question')
