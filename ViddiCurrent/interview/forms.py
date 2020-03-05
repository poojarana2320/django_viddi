from django import forms
import datetime
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm, PasswordChangeForm
from django.db import transaction
from turborecruit.settings import ADMIN_COMPANY_NAME
from interview.models import (
    User, Company, Interviewer, Question, Vacancy, Interview, Interviewee, Review)


class AdminSignUpForm(UserCreationForm):
    # company_name = forms.CharField()

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'email')

    def clean_email(self):
        # Get the email
        email = self.cleaned_data.get('email')

        # Check to see if any users already exist with this email as a username.
        try:
            match = User.objects.get(email=email)
        except User.DoesNotExist:
            # Unable to find a user, this is fine
            return email

        # A user was found with this as a username, raise an error.
        raise forms.ValidationError('This email address is already in use.')  

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.user_type = 1
        user.username = user.email
        user.save()
        # company_detail = Company.objects.get_or_create(
        #     name=self.cleaned_data.get('company_name'))[0]
        # interviewer = Interviewer.objects.create(
        #     user=user)
        return user


class AdminAuthenticationForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(AdminAuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs = {'required': True,
                                                'class': 'EmailAdd',
                                                'placeholder': 'Email',
                                                'id': 'email',
                                                'name': 'email',
                                                'type': 'text',
                                                'value': '',
                                                }
        self.fields['password'].widget.attrs = {'required': True,
                                                'class': 'PassAdd',
                                                'placeholder': 'Password',
                                                'id': 'password',
                                                'name': 'password',
                                                'type': 'password',
                                                'value': '',
                                                }


class UserAuthenticationForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(UserAuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs = {'required': True,
                                                'class': 'form-control',
                                                'placeholder': 'Username',
                                                'id': 'username',
                                                'name': 'username',
                                                'type': 'text',
                                                'value': '',
                                                }
        self.fields['password'].widget.attrs = {'required': True,
                                                'class': 'form-control',
                                                'placeholder': 'Password',
                                                'id': 'password',
                                                'name': 'password',
                                                'type': 'password',
                                                'value': '',
                                                }


class MyPasswordChangeForm(PasswordChangeForm):

    def __init__(self, *args, **kwargs):
        super(MyPasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs = {'required': True,
                                                    'class': 'EmailAdd',
                                                    'placeholder': 'Old Password',
                                                    'id': 'old_password',
                                                    'name': 'old_password',
                                                    'type': 'text',
                                                    'value': '',
                                                    }
        self.fields['new_password1'].widget.attrs = {'required': True,
                                                     'class': 'PassAdd',
                                                     'placeholder': 'New Password',
                                                     'id': 'new_password1',
                                                     'name': 'new_password1',
                                                     'type': 'password',
                                                     'value': '',
                                                     }
        self.fields['new_password2'].widget.attrs = {'required': True,
                                                     'class': 'PassAdd',
                                                     'placeholder': 'Confirm New Password',
                                                     'id': 'new_password2',
                                                     'name': 'new_password2',
                                                     'type': 'password',
                                                     'value': '',
                                                     }


class InterviewerSignUpForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super(InterviewerSignUpForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs = {"type": "text",
                                                  "name": "firstName",
                                                  "class": "form-control",
                                                  "required": True,
                                                  "placeholder": "Enter Firstname"
                                                  }
        self.fields['last_name'].widget.attrs = {"type": "text",
                                                 "name": "lastName",
                                                 "class": "form-control",
                                                 "required": True,
                                                 "placeholder": "Enter Lastname"
                                                 }
        self.fields['email'].widget.attrs = {"type": "email",
                                             "name": "email",
                                             "class": "form-control",
                                             "required": True,
                                             "onchange": "checkEmail(this)",
                                             "placeholder": "Enter email"
                                             }
        self.fields['password1'].widget.attrs = {"type": "password",
                                                 "name": "pass",
                                                 "class": "form-control",
                                                 "required": True,
                                                 "id=": "pass",
                                                 "placeholder": "Enter password"
                                                 }
        self.fields['password2'].widget.attrs = {"type": "password",
                                                 "name": "confirm_pass",
                                                 "class": "form-control",
                                                 "id": "confirm_pass",
                                                 "required": True,
                                                 "onchange": "confirmPassword()",
                                                 "placeholder": "Enter Confirm password"
                                                 }
        self.fields['user_type'].widget.attrs = {"class": "selectBox",
                                                 'required': True,
                                                 }
        self.fields['company_name'].choices = [(tempDict['id'], tempDict['name']) for tempDict in
                                               Company.objects.values()]
        self.fields['company_name'].widget.attrs = {'required': False,
                                                    "class": "selectBox",
                                                    "selected": "selected",
                                                    "value": "1",
                                                    }
        self.fields['user_type'].choices = [(index, value)
                                            for index, value in [(index, value)
                                                                 for index, value in self.fields['user_type'].choices
                                                                 if type(index) == int]
                                            if index < 10]

    company_name = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        required=False,
        initial=ADMIN_COMPANY_NAME
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'email',
                  'company_name', 'user_type')

    @transaction.atomic
    def save(self, user_obj=""):

        user = super().save(commit=False)
        user.username = user.email
        user.save()
        if user_obj.user_type == 1:
            company_detail = self.cleaned_data.get('company_name')
        else:
            company_detail = user_obj.working_organization.company
        interviewer = Interviewer.objects.create(
            user=user,
            company=company_detail)
        return user

    def clean_email(self):
        # Get the email
        email = self.cleaned_data.get('email')
        # Check to see if any users already exist with this email as a username.
        try:
            match = User.objects.get(email=email)
            print("-------in try------")
        except User.DoesNotExist:
            # Unable to find a user, this is fine
            print("-------in except------")
            return email

        # A user was found with this as a username, raise an error.
        raise forms.ValidationError('This email address is already in use.')


class InterviewerUpdateForm(UserChangeForm):

    def __init__(self, *args, **kwargs):
        super(InterviewerUpdateForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs = {"type": "text",
                                                  "name": "firstName",
                                                  "class": "form-control",
                                                  "required": True,
                                                  "placeholder": "Enter Firstname"
                                                  }
        self.fields['last_name'].widget.attrs = {"type": "text",
                                                 "name": "lastName",
                                                 "class": "form-control",
                                                 "required": True,
                                                 "placeholder": "Enter Lastname"
                                                 }
        self.fields['email'].widget.attrs = {"type": "email",
                                             "name": "email",
                                             "class": "form-control",
                                             "onchange": "checkEmail(this)",
                                             "placeholder": "Enter email",
                                             'readonly': "readonly",
                                             }
        self.fields['user_type'].widget.attrs = {"class": "selectBox",
                                                 'required': True,
                                                 }
        self.fields['user_type'].choices = [(index, value)
                                            for index, value in [(index, value)
                                                                 for index, value in self.fields['user_type'].choices
                                                                 if type(index) == int]
                                            if index < 10]

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'email',
                  'user_type')

    @transaction.atomic
    def save(self, user_obj=""):
        user = super().save(commit=True)
        user.save()
        return user


class CompanyUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CompanyUpdateForm, self).__init__(*args, **kwargs)

        self.fields['name'].widget.attrs = {"type": "name",
                                            "name": "mCompany_name",
                                            "class": "form-control",
                                            "required": True,
                                            }
        # self.fields['img'].widget.attrs = {"type": "img",
        #                                    "name": "img",
        #                                    "class": "form-control",
        #                                    }

        self.fields['about'].widget.attrs = {"type": "about",
                                             "name": "about_company",
                                             "class": "form-control",
                                             }

        self.fields['email'].widget.attrs = {"type": "email",
                                             "name": "email",
                                             "class": "form-control",
                                             "placeholder": "Enter email",
                                             }

        self.fields['address'].widget.attrs = {"type": "address",
                                               "name": "address",
                                               "class": "form-control",
                                               "placeholder": "Enter address",
                                               }

    class Meta(UserCreationForm.Meta):
        model = Company
        fields = ('name', 'img', 'email', 'about', 'address',)


class CompanyCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CompanyCreateForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs = {"type": "name",
                                            "name": "mCompany",
                                            "class": "form-control",
                                            "placeholder": "Enter Company name",
                                            }

        self.fields['img'].widget.attrs = {"type": "img",
                                           "name": "img",
                                           "class": "form-control",
                                           }

        self.fields['about'].widget.attrs = {"type": "about",
                                             "name": "about_company",
                                             "class": "form-control",
                                             }

        self.fields['email'].widget.attrs = {"type": "email",
                                             "name": "email",
                                             "class": "form-control",
                                             "placeholder": "Enter email",
                                             }

        self.fields['address'].widget.attrs = {"type": "address",
                                               "name": "address",
                                               "class": "form-control",
                                               "placeholder": "Enter address",
                                               }

    class Meta(UserCreationForm.Meta):
        model = Company
        fields = ('name', 'img', 'about', 'email', 'address',)

    @transaction.atomic
    def save(self, user_obj=""):
        company = super().save(commit=False)
        company.save()
        return company


class CompanyEmailForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CompanyEmailForm, self).__init__(*args, **kwargs)

        self.fields['email_template'].widget.attrs = {"id": "id_email_template",
                                                      "name": "email_template",
                                                      "class": "form-group",
                                                      "style": "margin-top: 0px; margin-bottom: 0px; height: 230px;",
                                                      }

    class Meta(UserCreationForm.Meta):
        model = Company
        fields = ('email_template',)


class QuestionCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(QuestionCreateForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget.attrs = {"type": "text",
                                            "name": "mainQuestion",
                                            "class": "form-control",
                                            "required": True,
                                            "id": "practiceQn",
                                            "placeholder": "Enter Question",
                                            "value": "",
                                            }
        self.fields['time'].widget.attrs = {"type": "text",
                                            "name": "mQuestion_time",
                                            "class": "form-control",
                                            "required": True,
                                            "id": "practiceQnTm",
                                            "placeholder": "Enter question time",
                                            "value": "30",
                                            }

    class Meta(UserCreationForm.Meta):
        model = Question
        fields = ('text', 'time', )

    @transaction.atomic
    def save(self, user_obj=""):
        question = super().save(commit=False)
        question.question_owner = User.objects.filter(
            username=user_obj.username)[0]
        question.owner_company = user_obj.working_organization.company
        question.save()
        return question


class QuestionUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(QuestionUpdateForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget.attrs = {"type": "text",
                                            "name": "mainQuestion",
                                            "class": "form-control",
                                            "required": True,
                                            "id": "practiceQn",
                                            "placeholder": "Enter Question",
                                            }
        self.fields['time'].widget.attrs = {"type": "text",
                                            "name": "mQuestion_time",
                                            "class": "form-control",
                                            "required": True,
                                            "id": "practiceQnTm",
                                            "placeholder": "Enter question time",
                                            }

    class Meta(UserCreationForm.Meta):
        model = Question
        fields = ('text', 'time',)

    @transaction.atomic
    def save(self, user_obj=""):
        question = super().save(commit=False)
        # question.question_owner = User.objects.filter(username=user_obj.username)[0]
        # question.owner_company = user_obj.working_organization.company
        question.save()
        return question


class VacancyCreateForm(forms.ModelForm):
    def __init__(self, data=None, *args, **kwargs):
        if data is not None:
            data = data.copy()  # make it mutable
            data['start_date'] = datetime.date(int(data['start_date'].split("/")[2]),
                                               int(data['start_date'].split(
                                                   "/")[1]),
                                               int(data['start_date'].split("/")[0]))
            data['l_date'] = datetime.date(int(data['l_date'].split("/")[2]),
                                           int(data['l_date'].split("/")[1]),
                                           int(data['l_date'].split("/")[0]))
        super(VacancyCreateForm, self).__init__(data, *args, **kwargs)
        self.fields['position'].widget.attrs = {"type": "text",
                                                "name": "post",
                                                "class": "form-control",
                                                "required": True,
                                                "placeholder": "Enter post",
                                                "value": "",
                                                }
        self.fields['description'].widget.attrs = {"type": "text",
                                                   "name": "description",
                                                   "class": "form-control",
                                                   "required": False,
                                                   "placeholder": "Interview Description",
                                                   }
        self.fields['status'].widget.attrs = {"type": "text",
                                              "name": "post_status",
                                              "class": "form-control",
                                              "required": True,
                                              }
        # self.fields['start_date'].widget.attrs = {"type": "date",
        #                                           "name": "start_date",
        #                                           "class": "form-control",
        #                                           "required": True,
        #                                           "placeholder": "Enter start date",
        #                                           }
        # self.fields['end_date'].widget.attrs = {"type": "date",
        #                                         "name": "l_date",
        #                                         "class": "form-control",
        #                                         "required": True,
        #                                         "placeholder": "Enter last date",
        #                                         }
        self.fields['organisation'].widget.attrs = {"name": "organisation",
                                                    "class": "form-control",
                                                    "required": False,
                                                    "id": "organisation",
                                                    "selected": "selected",
                                                    "value": "1",
                                                    }
        self.fields['organisation'].choices = [(tempDict['id'], tempDict['name']) for tempDict in
                                               Company.objects.values()]

    organisation = forms.ModelChoiceField(
        queryset=Company.objects.all(),
        required=False,
        initial=ADMIN_COMPANY_NAME
    )

    class Meta(UserCreationForm.Meta):
        model = Vacancy
        fields = ('position', 'description', 'status', 'organisation')

    @transaction.atomic
    def save(self, user_obj=""):
        vacancy = super().save(commit=False)
        vacancy.start_date = self.data.get('start_date')
        vacancy.end_date = self.data.get('l_date')
        vacancy.vacancy_owner = User.objects.filter(
            username=user_obj.username)[0]
        if user_obj.user_type == 1:
            vacancy.organisation = vacancy.organisation
        else:
            vacancy.organisation = user_obj.working_organization.company
        vacancy.save()
        return vacancy


class VacancyUpdateForm(forms.ModelForm):

    def __init__(self, data=None, *args, **kwargs):
        if data is not None:
            data = data.copy()  # make it mutable
            data['start_date'] = datetime.date(int(data['start_date'].split("/")[2]),
                                               int(data['start_date'].split(
                                                   "/")[1]),
                                               int(data['start_date'].split("/")[0]))
            data['end_date'] = datetime.date(int(data['end_date'].split("/")[2]),
                                             int(data['end_date'].split(
                                                 "/")[1]),
                                             int(data['end_date'].split("/")[0]))
        super(VacancyUpdateForm, self).__init__(data, *args, **kwargs)
        self.fields['position'].widget.attrs = {"type": "text",
                                                "name": "post",
                                                "class": "form-control",
                                                "required": True,
                                                "placeholder": "Enter post",
                                                "value": "",
                                                }
        self.fields['description'].widget.attrs = {"type": "text",
                                                   "name": "description",
                                                   "class": "form-control",
                                                   "required": False,
                                                   "placeholder": "Interview Description",
                                                   }
        self.fields['status'].widget.attrs = {"type": "text",
                                              "name": "post_status",
                                              "class": "form-control",
                                              "required": True,
                                              }
        self.fields['start_date'].widget.attrs = {"id": "datepicker1",
                                                  "name": "start_date",
                                                  "class": "form-control",
                                                  "required": False,
                                                  "placeholder": "Enter start date",
                                                  }
        self.fields['end_date'].widget.attrs = {"id": "datepicker2",
                                                "name": "l_date",
                                                "class": "form-control",
                                                "required": False,
                                                "placeholder": "Enter last date",
                                                }

    class Meta(UserCreationForm.Meta):
        model = Vacancy
        fields = ('position', 'description', 'status',
                  'start_date', 'end_date', )

    @transaction.atomic
    def save(self, user_obj=""):
        vacancy = super().save(commit=False)
        # vacancy.vacancy_owner = User.objects.filter(username=user_obj.username)[0]
        # if user_obj.user_type == 1:
        #     vacancy.organisation = vacancy.organisation
        # else:
        #     vacancy.organisation = user_obj.working_organization.company
        vacancy.save()
        return vacancy


class InterviewCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(InterviewCreateForm, self).__init__(*args, **kwargs)
        self.fields['position_name'].widget.attrs = {"name": "post_applied",
                                                     "class": "form-control Vacan_cy",
                                                     "required": True,
                                                     "id": "post",
                                                     "onchange": "setPost(this)",
                                                     }
        self.fields['questions'].widget.attrs = {"type": "hidden",
                                                 "name": "qbj_question",
                                                 "required": False,
                                                 "id": "qbj_question",
                                                 "value": "",
                                                 }

    position_name = forms.ModelChoiceField(
        queryset=Vacancy.objects.filter(status='Active'),
        required=False,
        initial=""
    )

    questions = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
        initial=""
    )

    class Meta(UserCreationForm.Meta):
        model = Interview
        fields = ('position_name', 'questions')

    @transaction.atomic
    def save(self, user_obj=""):
        interview = super().save(commit=False)
        interview.interview_owner = Interviewer.objects.filter(user=user_obj)[
            0]
        interview.interview_organisation = \
            Company.objects.filter(id=Vacancy.objects.filter(id=interview.position_name_id).values()[0]['organisation_id'])[
                0]
        interview.save()
        for index, values in eval(self.cleaned_data.get('questions')).items():
            if len(Question.objects.filter(question_owner=user_obj).filter(text=values['question'])) > 0:
                interview.questions.add(
                    Question.objects.filter(question_owner=user_obj).filter(
                        text=values['question'])[0],
                    through_defaults={'index': int(index)})
            elif len(Question.objects.filter(owner_company=user_obj.working_organization.company).filter(
                    text=values['question'])) > 0:
                interview.questions.add(
                    Question.objects.filter(owner_company=user_obj.working_organization.company).filter(
                        text=values['question'])[0],
                    through_defaults={'index': int(index)})
            elif len(Question.objects.filter(text=values['question'])) > 0:
                interview.questions.add(Question.objects.filter(text=values['question'])[0],
                                        through_defaults={'index': int(index)})
            else:
                interview.questions.add(Question.objects.get_or_create(
                    text=values['question'], time=values['time'],
                    question_owner=user_obj,
                    owner_company=user_obj.working_organization.company)[
                    0], through_defaults={'index': int(index)})
        return interview


class InterviewUpdateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(InterviewUpdateForm, self).__init__(*args, **kwargs)
        self.fields['position_name'].widget.attrs = {"name": "post_applied",
                                                     "class": "form-control Vacan_cy",
                                                     "required": True,
                                                     "id": "post",
                                                     "onchange": "setPost(this)",
                                                     }
        self.fields['question_s'].widget.attrs = {"type": "hidden",
                                                  "name": "qbj_question",
                                                  "required": False,
                                                  "id": "qbj_question",
                                                  "value": "",
                                                  }

    position_name = forms.ModelChoiceField(
        queryset=Vacancy.objects.all(),
        required=False,
        initial=""
    )

    question_s = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
        initial=""
    )

    class Meta(UserCreationForm.Meta):
        model = Interview
        fields = ('position_name', 'question_s')

    @transaction.atomic
    def save(self, user_obj=""):
        interview = super().save(commit=False)
        interview.interview_owner = Interviewer.objects.filter(user=user_obj)[
            0]
        interview.interview_organisation = \
            Company.objects.filter(id=Vacancy.objects.filter(id=interview.position_name_id).values()[0]['organisation_id'])[
                0]
        interview.save()
        for index, values in eval(self.cleaned_data.get('question_s')).items():
            if len(Question.objects.filter(question_owner=user_obj).filter(text=values['question'])) > 0:
                interview.questions.add(
                    Question.objects.filter(question_owner=user_obj).filter(text=values['question'])[0], through_defaults={'index': int(index)})
            elif len(Question.objects.filter(owner_company=user_obj.working_organization.company).filter(
                    text=values['question'])) > 0:
                interview.questions.add(
                    Question.objects.filter(owner_company=user_obj.working_organization.company).filter(
                        text=values['question'])[0], through_defaults={'index': int(index)})
            elif len(Question.objects.filter(text=values['question'])) > 0:
                interview.questions.add(Question.objects.filter(text=values['question'])[0],
                                        through_defaults={'index': int(index)})
            else:
                interview.questions.add(Question.objects.get_or_create(
                    text=values['question'], time=values['time'],
                    question_owner=user_obj,
                    owner_company=user_obj.working_organization.company)[0], through_defaults={'index': int(index)})
        return interview


class IntervieweeSignUpForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(IntervieweeSignUpForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs = {"type": "text",
                                            "name": "name",
                                            "class": "form-control",
                                            "required": True,
                                            "placeholder": "Enter name"
                                            }
        self.fields['email'].widget.attrs = {"type": "email",
                                             "name": "email",
                                             "class": "Email_Inter",
                                             "required": True,
                                             "placeholder": "Enter email"
                                             }
        self.fields['phone'].widget.attrs = {"type": "text",
                                             "name": "phone",
                                             "class": "form-control",
                                             "required": False,
                                             "placeholder": "Phone"
                                             }

    email = forms.EmailField(max_length=254)

    class Meta:
        model = Interviewee
        fields = ('name', 'email', 'phone', )
