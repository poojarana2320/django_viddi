import os
import codecs
import datetime
import shutil
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'turborecruit.settings')



import django
django.setup()

from interview.models import User, Company, Interviewer, Question, Vacancy, Interview, Review


def set_users(data_dict):
    for key in sorted(data_dict.keys()):
        value = data_dict[key]
        try:
            c = User.objects.get_or_create(id=key,
                                       username=value['username'],
                                       first_name=value['first_name'],
                                       last_name=value['last_name'],
                                       user_type=value['user_type'],
                                       email=value['email'],
                                       password=value['password'],
                                       )[0]
            c.set_password(value['password'])
            c.save()
        except:
            pass


def set_companies(data_dict):
    for key, value in data_dict.items():
        try:
            c = Company.objects.get_or_create(name=value['name'],
                                              id=value['id'],
                                          )[0]
            c.save()
        except:
            pass


def set_interviewer(data_dict):
    for key, value in data_dict.items():
        try:
            company_name = ""
            for _, cid in companies.items():
                if cid['id'] == value['company_id']:
                    company_name = cid['name']
            c = Interviewer.objects.get_or_create(
                user_id=User.objects.filter(email=users[value['user_id']]['username'])[0].id,
                company_id=Company.objects.filter(name=company_name)[0].id)[0]
            c.save()
        except:
            pass


def set_questions(data_dict):
    for key, value in data_dict.items():
        # 0: {'question_owner_id': 1, 'owner_company_id': 1, 'text': 'Admin Question - Anvaya - 1', 'time': 35}
        try:
            company_name = ""
            for _, cid in companies.items():
                if cid['id'] == value['owner_company_id']:
                    company_name = cid['name']
            c = Question.objects.get_or_create(
                question_owner_id=User.objects.filter(email=users[value['question_owner_id']]['username'])[0].id,
                owner_company_id=Company.objects.filter(name=company_name)[0].id,
                text=value['text'],
                time=value['time'],
               )[0]
            c.save()
        except:
            pass


def set_vacancies(data_dict):
    for key, value in data_dict.items():
        # 0: {'vacancy_owner_id': 1, 'owner_company_id': 2, 'position': 'Super Admin Vacancy - eLeoRex', 'descri
        company_name = ""
        for _, cid in companies.items():
            if cid['id'] == value['owner_company_id']:
                company_name = cid['name']
        try:
            c = Vacancy.objects.get_or_create(
                vacancy_owner_id=User.objects.filter(email=users[value['vacancy_owner_id']]['username'])[0].id,
                organisation_id=Company.objects.filter(name=company_name)[0].id,
                position=value['position'],
                description=value['description'],
                count=value['count'],
                status=value['status'],
                start_date=value['start_date'],
                end_date=value['end_date'],
            )[0]

            c.save()
        except:
            pass


def get_users():
    user_dict = {}
    for index, user in enumerate(User.objects.all()):
        sub_dict = {}
        sub_dict['username'] = user.username
        sub_dict['first_name'] = user.first_name
        sub_dict['last_name'] = user.last_name
        sub_dict['user_type'] = user.user_type
        sub_dict['email'] = user.email
        sub_dict['password'] = "pass@123"
        user_dict[user.id] = sub_dict
    return user_dict


def get_companies():
    compnay_dict = {}
    for index, company in enumerate(Company.objects.all()):
        sub_dict = {}
        sub_dict['id'] = company.id
        sub_dict['name'] = company.name
        compnay_dict[index] = sub_dict
    return compnay_dict


def get_interviewer():
    interviewer_dict = {}
    for index, interviewer in enumerate(Interviewer.objects.all()):
        sub_dict = {}
        sub_dict['user_id'] = interviewer.user_id
        sub_dict['company_id'] = interviewer.company_id
        interviewer_dict[index] = sub_dict
    return interviewer_dict


def get_questions():
    question_dict = {}
    for index, question in enumerate(Question.objects.all()):
        sub_dict = {}
        sub_dict['question_owner_id'] = question.question_owner_id
        sub_dict['owner_company_id'] = question.owner_company_id
        sub_dict['text'] = question.text
        sub_dict['time'] = question.time
        question_dict[index] = sub_dict
    return question_dict


def get_vacancies():
    vacancy_dict = {}
    for index, vacancy in enumerate(Vacancy.objects.all()):
        sub_dict = {}
        sub_dict['vacancy_owner_id'] = vacancy.vacancy_owner_id
        sub_dict['owner_company_id'] = vacancy.organisation_id
        sub_dict['position'] = vacancy.position
        sub_dict['description'] = vacancy.description
        sub_dict['count'] = vacancy.count
        sub_dict['status'] = vacancy.status
        sub_dict['start_date'] = vacancy.start_date
        sub_dict['end_date'] = vacancy.end_date
        vacancy_dict[index] = sub_dict
    return vacancy_dict


def remove_old_db():
    os.system("rm -rf " + os.path.join(os.getcwd(),'turborecruit', '__pycache__'))
    os.system("rm -rf " + os.path.join(os.getcwd(), 'interview', '__pycache__'))
    os.system("rm -rf " + os.path.join(os.getcwd(), 'interview', 'migrations'))
    os.system("rm -rf " + os.path.join(os.getcwd(), 'db.sqlite3'))

#7 - ICAA
#8 - MCC
#9 - Yourtown
#10 - Readytech
#11 - FibreHR
#12 - Stillwell
#13 - Worksafe
#14 - TotalTools
#companies = {1: {'id': 7, 'name': 'ICAA'}, 2: {'id': 8, 'name': 'MCC'}, 3: {'id': 9, 'name': 'Yourtown'}, 4: {'id': 10, 'name': 'Readytech'}, 5: {'id': 11, 'name': 'Hoban Recruitment'}}
companies = {1: {'id': 7, 'name': 'ICAA'}, 2: {'id': 8, 'name': 'MCC'}, 3: {'id': 9, 'name': 'Readytech'}, 4: {'id': 10, 'name': 'FibreHR'}, 5: {'id': 11, 'name': 'Stillwell'}, 6: {'id': 12, 'name': 'Worksafe'}, 7: {'id': 13, 'name': 'TotalTools'}}
set_companies(companies)
