import json
import MySQLdb
from dg.settings import DATABASES
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth
from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.db.models import Count, Sum, F
from django.core.serializers.json import DjangoJSONEncoder

import pandas
from tastypie.models import ApiKey, create_api_key
from models import Training, Score, Trainer, Question, Assessment
from activities.models import Screening, PersonAdoptPractice, PersonMeetingAttendance
from geographies.models import State
from django.db import connection
import datetime
from training.management.databases.utility import multiprocessing_dict, multiprocessing_list
from training.management.databases.get_sql_queries import *
from training.log.training_log import get_latest_timestamp

# Create your views here.
@csrf_exempt
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            try:
                api_key = ApiKey.objects.get(user=user)
            except ApiKey.DoesNotExist:
                api_key = ApiKey.objects.create(user=user)
                api_key.save()
            log_obj = get_latest_timestamp()
            if log_obj == None:
                timestamp = datetime.datetime.utcnow()
            else:
                timestamp = log_obj.timestamp
            trainer = Trainer.objects.filter(training_user__user__id = user.id).first()
            return HttpResponse(json.dumps({'ApiKey':api_key.key,'timestamp':str(timestamp),'TrainerId':trainer.id}))
        else:
            return HttpResponse("0",status=401)
    else:
        return HttpResponse("0",status=403)
    return HttpResponse("0",status=404)

def extractFiltersFromRequest(request):
    if 'start_date' in request.GET and 'end_date' in request.GET:
        start_date = str(request.GET['start_date'])
        end_date = str(request.GET['end_date'])
    else:
        start_date = '2015-01-01'
        end_date = '2017-05-30'
    if 'apply_filter' in request.GET:
        apply_filter = True if request.GET['apply_filter'] == 'true' else False
    else :
        apply_filter = False
    if 'chartType' in request.GET and 'chartName' in request.GET:
        chart_type =  str(request.GET.get('chartType'))
        chart_name = str(request.GET.get('chartName'))
    else:
        chart_type = ''
        chart_name = ''
    trainers_list = request.GET.getlist('Trainer')
    states_list = request.GET.getlist('State')

    filter_args = {}
    filter_args['start_date'] = start_date
    filter_args['end_date'] = end_date
    filter_args['apply_filter'] = apply_filter
    filter_args['trainers_list'] = trainers_list
    filter_args['states_list'] = states_list
    filter_args['chart_name'] = chart_name
    filter_args['chart_type'] = chart_type

    return filter_args

def getPandasDataframe(sql_query):
    db_connection = MySQLdb.connect(host='localhost',
                                        user=DATABASES['default']['USER'],
                                        passwd=DATABASES['default']['PASSWORD'],
                                        db=DATABASES['default']['NAME'],
                                        charset='utf8',
                                        use_unicode=True)
    result = pandas.read_sql_query(sql_query, con=db_connection)
    return result

@csrf_exempt
def getFilterData(request):
    trainers_list = Trainer.objects.annotate(value=F('name')).values('id','value').order_by('value')
    states_list = State.objects.annotate(value=F('state_name')).values('id','value').order_by('value')
    response_list = []
    trainer_dict = {'name':'Trainer', 'visible':True, 'data':list(trainers_list)}
    state_dict = {'name':'State', 'visible':True, 'data':list(states_list)}
    date_dict = {'name':'date', 'visible':True}
    response_list.extend([trainer_dict, state_dict, date_dict])
    json_data = json.dumps(response_list)
    return HttpResponse(json_data)

@csrf_exempt
def getData(request):
    filter_args = extractFiltersFromRequest(request)
    query_list = []

    recent_days_count = [120,180,365]
    recent_data_dict = {}

    # No of Trainings
    training_query = get_training_data_sql(**filter_args)
    result = getPandasDataframe(training_query)
    result['date'] = result['date'].astype('datetime64[ns]')
    for days in recent_days_count:
        today = datetime.datetime.today() - datetime.timedelta(days=days)
        data = pandas.Series(pandas.DataFrame(result.where((result['date'] >= today))).sum(numeric_only=True))
        recent_data_dict[str(days) + 'days'] = []
        recent_data_dict[str(days) + 'days'].append({'placeHolder':'recent','tagName':'Number of Trainings','value':data['Trainings']})
    # query_list.extend(training_query)

    # No of Mediators
    mediator_query = get_mediators_data_sql(**filter_args)
    query_list.extend(mediator_query)

    # Pass Percentage
    pass_percent_query = get_pass_perc_data_sql(**filter_args)
    query_list.extend(pass_percent_query)

    # Avg Score
    avg_score_query = get_avg_score_data_sql(**filter_args)
    query_list.extend(avg_score_query)

    results = multiprocessing_list(query_list = query_list)
    data = json.dumps({'data' : results})
    return HttpResponse(data)


def dashboard(request):
    # return render(request, 'src/index.html')
    return render(request, 'app_dashboards/training_dashboard.html')

def filter_data(request):
    assessments = Assessment.objects.values('id', 'name')
    trainers = Trainer.objects.values('id', 'name')
    states = State.objects.values('id','state_name')
    filter_args = {}
    filter_args['score__in'] = [0, 1]
    score_queryset = Score.objects.filter(**filter_args)
    participants = score_queryset.values('participant__id').distinct()
    num_trainings = score_queryset.values('training_id').distinct().count()
    num_pass = score_queryset.values('participant').annotate(Sum('score'), Count('score'))
    num_participants = participants.count()
    data_dict = {'assessments': list(assessments), 'trainers': list(trainers), 'states': list(states), 'num_trainings': num_trainings, 'num_participants': num_participants, 'num_pass': list(num_pass)}
    data = json.dumps(data_dict)
    return HttpResponse(data)

def date_filter_data(request):

    start_date = request.GET['start_date']
    end_date = request.GET['end_date']
    assessment_ids = request.GET.getlist('assessment_ids[]')
    trainer_ids = request.GET.getlist('trainer_ids[]')
    state_ids = request.GET.getlist('state_ids[]')
    filter_args = {}
    if(start_date !=""):
        filter_args["training__date__gte"] = start_date
    if(end_date != ""):
        filter_args["training__date__lte"] = end_date
    filter_args['training__assessment__id__in'] = assessment_ids
    filter_args["training__trainer__id__in"] = trainer_ids
    filter_args["participant__district__state__id__in"] = state_ids
    filter_args['score__in'] = [0, 1]
    score_queryset = Score.objects.filter(**filter_args)
    participants = score_queryset.values_list('participant__id', flat=True).distinct()
    num_trainings = score_queryset.values('training_id').distinct().count()
    num_pass = score_queryset.values('participant').annotate(Sum('score'), Count('score'))
    num_participants = participants.count()

    data_dict = {'num_trainings': num_trainings, 'num_participants': num_participants, 'num_pass': list(num_pass)}
    data = json.dumps(data_dict)
    return HttpResponse(data)

def trainer_wise_data(request):
    start_date = request.GET['start_date']
    end_date = request.GET['end_date']
    assessment_ids = request.GET.getlist('assessment_ids[]')
    trainer_ids = request.GET.getlist('trainer_ids[]')
    state_ids = request.GET.getlist('state_ids[]')
    filter_args = {}
    trainer_wise_avg_score = {}
    trainer_wise_avg_score_list = []
    if(start_date !=""):
        filter_args["training__date__gte"] = start_date
    if(end_date != ""):
        filter_args["training__date__lte"] = end_date
    filter_args["training__assessment__id__in"] = assessment_ids
    filter_args["training__trainer__id__in"] = trainer_ids
    filter_args["participant__district__state__id__in"] = state_ids
    filter_args["score__in"] = [1, 0]
    score_obj = Score.objects.filter(**filter_args)
    trainer_list_participant_training_count = score_obj.values('training__trainer__name').order_by('training__trainer__name').annotate(Count('participant', distinct=True) , Sum('score'), Count('score'), Count('training__id', distinct=True),all_participant_count=Count('participant', distinct=False))
    trainer_list_participant_count = score_obj.values('training__trainer__name', 'training_id').order_by('training__trainer__name').annotate(Count('participant', distinct=True ), Sum('score'))

    for trainer in trainer_list_participant_count :
        trainer_name = trainer['training__trainer__name']
        if(trainer_name not in trainer_wise_avg_score) :
            trainer_wise_avg_score[trainer_name] = {}
            trainer_wise_avg_score[trainer_name]['participant_count'] = trainer['participant__count']
            trainer_wise_avg_score[trainer_name]['score_sum'] = trainer['score__sum']
        else :
            trainer_wise_avg_score[trainer_name]['participant_count'] += trainer['participant__count']
            trainer_wise_avg_score[trainer_name]['score_sum'] += trainer['score__sum']

    for trainer_score in sorted(trainer_wise_avg_score) :
        json_obj = {}
        json_obj[trainer_score] = trainer_wise_avg_score[trainer_score]
        trainer_wise_avg_score_list.append(json_obj)

    mediator_list = Score.objects.filter(**filter_args).values('training__trainer__name', 'participant').order_by('training__trainer__name').annotate(Sum('score'), Count('score'))
    data_dict = {'trainer_list': list(trainer_list_participant_training_count), 'mediator_list': list(mediator_list), 'trainer_wise_average_score_data' : trainer_wise_avg_score_list}
    data = json.dumps(data_dict)
    return HttpResponse(data)

def question_wise_data(request):
    start_date = request.GET['start_date']
    end_date = request.GET['end_date']
    assessment_ids = request.GET.getlist('assessment_ids[]')
    trainer_ids = request.GET.getlist('trainer_ids[]')
    state_ids = request.GET.getlist('state_ids[]')
    question_data_dict = {}
    language_count = 0
    language_eng_id = 2
    filter_args = {}
    if(start_date !=""):
        filter_args["training__date__gte"] = start_date
    if(end_date != ""):
        filter_args["training__date__lte"] = end_date
    filter_args["training__assessment__id__in"] = assessment_ids
    filter_args["training__trainer__id__in"] = trainer_ids
    filter_args["participant__district__state__id__in"] = state_ids
    filter_args["score__in"] = [1, 0]
    question_list = Score.objects.filter(**filter_args).values('question__text', 'question__language__id', 'question__section', 'question__serial').order_by('question__language_id', 'question__section', 'question__serial').annotate(Sum('score'), Count('score'), Count('participant', distinct=True))
    language_text_eng = Question.objects.filter(language_id = language_eng_id, assessment_id__in=assessment_ids).values('text', 'section', 'serial').order_by('section', 'serial')
    question_data_dict = {'question_list' : list(question_list), 'question_language_text_eng':list(language_text_eng)}
    data = json.dumps(question_data_dict)
    return HttpResponse(data)

def state_wise_data(request):
    start_date = request.GET['start_date']
    end_date = request.GET['end_date']
    assessment_ids = request.GET.getlist('assessment_ids[]')
    trainer_ids = request.GET.getlist('trainer_ids[]')
    state_ids = request.GET.getlist('state_ids[]')
    filter_args = {}
    state_wise_avg_score = {}
    state_wise_avg_score_list = []
    if(start_date !=""):
        filter_args["training__date__gte"] = start_date
    if(end_date != ""):
        filter_args["training__date__lte"] = end_date
    filter_args["training__assessment__id__in"] = assessment_ids
    filter_args["training__trainer__id__in"] = trainer_ids
    filter_args["participant__district__state__id__in"] = state_ids
    filter_args["score__in"] = [1, 0]

    score_obj = Score.objects.filter(**filter_args)
    state_list_participant_training_count = score_obj.values('participant__district__state__state_name').order_by('participant__district__state__state_name').annotate(Sum('score'), Count('score'), Count('participant', distinct=True), Count('training__id', distinct=True))
    state_list_participant_count = score_obj.values('participant__district__state__state_name', 'training_id').order_by('participant__district__state__state_name').annotate(Sum('score'), Count('score'), Count('participant', distinct=True))

    for state in state_list_participant_count :
        state_name = state['participant__district__state__state_name']
        if(state_name not in state_wise_avg_score) :
            state_wise_avg_score[state_name] = {}
            state_wise_avg_score[state_name]['participant_count'] = state['participant__count']
            state_wise_avg_score[state_name]['score_sum'] = state['score__sum']
        else :
            state_wise_avg_score[state_name]['participant_count'] += state['participant__count']
            state_wise_avg_score[state_name]['score_sum'] += state['score__sum']

    for state_score in sorted(state_wise_avg_score) :
        json_obj = {}
        json_obj[state_score] = state_wise_avg_score[state_score]
        state_wise_avg_score_list.append(json_obj)

    mediator_list = Score.objects.filter(**filter_args).values('participant__district__state__state_name', 'participant').order_by('participant__district__state__state_name').annotate(Sum('score'), Count('score'))
    data_dict = {'state_list': list(state_list_participant_training_count), 'mediator_list': list(mediator_list), 'state_wise_avg_score_data' : list(state_wise_avg_score_list)}
    data = json.dumps(data_dict)
    return HttpResponse(data)


def month_wise_data(request):
    start_date = request.GET['start_date']
    end_date = request.GET['end_date']
    current_year = datetime.date.today().year
    start_date = datetime.date(current_year, 01, 01)
    end_date = datetime.date(current_year, 12, 31)
    assessment_ids = request.GET.getlist('assessment_ids[]')
    trainer_ids = request.GET.getlist('trainer_ids[]')
    state_ids = request.GET.getlist('state_ids[]')
    filter_args = {}
    if(start_date !=""):
        filter_args["training__date__gte"] = start_date
    if(end_date != ""):
        filter_args["training__date__lte"] = end_date
    filter_args["training__assessment__id__in"] = assessment_ids
    filter_args["training__trainer__id__in"] = trainer_ids
    filter_args["participant__district__state__id__in"] = state_ids
    filter_args["score__in"] = [1, 0]

    month_data_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    truncate_date = connection.ops.date_trunc_sql('month', 'date')
    training_month_data = Training.objects.extra({'month':truncate_date})
    training_list = list(Score.objects.values_list('training_id', flat=True).distinct())
    month_wise_training_data = training_month_data.filter(id__in=training_list, date__gte=start_date, date__lte=end_date).values('month').annotate(Count('id')).order_by('month')

    maximum = -1
    for training_data in month_wise_training_data:
        month = training_data['month'].month
        training_count = training_data['id__count']
        month_data_list[month - 1] = training_count
        maximum = max(maximum, month)

    data_dict = {'trainings':'Number of Trainings','month_training_list':month_data_list[:maximum]}
    data = json.dumps(data_dict)
    return HttpResponse(data)

def number_of_trainings(chart_name, result):
    final_data_list = {}
    state_grouped_data = result.groupby(['state']).sum().reset_index()
    try:
        outer_data = {'outerData': {'series':[],'categories':state_grouped_data['state'].tolist()}}

        temp_dict_outer = {'name':'Trainings','data':[]}
        for row in state_grouped_data.iterrows():
            temp_dict_outer['data'].append({'name':row[1].state,'y':int(row[1].trainings),'drilldown':row[1].state +' trainings'})

        outer_data['outerData']['series'].append(temp_dict_outer)
        final_data_list[chart_name] = outer_data
        inner_data = {'innerData': []}

        trainer_training_dict = {name:dict(zip(g['trainer'],g['trainings'])) for name,g in result.groupby('state')}
        for key,value in trainer_training_dict.iteritems():
            temp_dict_inner = {'data':[]}
            temp_dict_inner['name'] = key
            temp_dict_inner['id'] = key + ' trainings'
            for k, v in value.iteritems():
                temp_dict_inner['data'].append([k,v])
            inner_data['innerData'].append(temp_dict_inner)

        final_data_list[chart_name].update(inner_data)
    except:
        final_data_list['error']="No data found for the filters applied"
    return final_data_list

def pandas_default_aggregation(chart_name, result):
    final_data_list = {}
    state_grouped_data = result.groupby(['state']).sum().reset_index()
    try:
        outer_data = {'outerData': {'series':[],'categories':state_grouped_data['state'].tolist()}}
        temp_dict_outer = {'name':'Mediators','data':[]}
        for row in state_grouped_data.iterrows():
            temp_dict_outer['data'].append({'name':row[1].state,'y':int(row[1].mediators),'drilldown':row[1].state+' mediators'})
        outer_data['outerData']['series'].append(temp_dict_outer)

        temp_dict_outer = {'name':'Above70','data':[]}
        for row in state_grouped_data.iterrows():
            temp_dict_outer['data'].append({'name':row[1].state,'y':int(row[1].Above70),'drilldown':row[1].state+' above70'})

        outer_data['outerData']['series'].append(temp_dict_outer)
        final_data_list[chart_name] = outer_data
        inner_data = {'innerData': []}
        trainer_mediators_dict = {name: dict(zip(g['trainer'],g['mediators'])) for name,g in result.groupby('state')}
        trainer_pass_dict = {name: dict(zip(g['trainer'],g['Above70'])) for name,g in result.groupby('state')}
        for key, value in trainer_mediators_dict.iteritems():
            temp_dict_inner = {'data':[]}
            temp_dict_inner['name'] = key
            temp_dict_inner['id'] = key + ' mediators'
            for k, v in value.iteritems():
                temp_dict_inner['data'].append([k,v])
            inner_data['innerData'].append(temp_dict_inner)

        for key, value in trainer_pass_dict.iteritems():
            temp_dict_inner = {'data':[]}
            temp_dict_inner['name'] = key
            temp_dict_inner['id'] = key + ' above70'
            for k, v in value.iteritems():
                temp_dict_inner['data'].append([k,v])
            inner_data['innerData'].append(temp_dict_inner)

        final_data_list[chart_name].update(inner_data)
    except:
        final_data_list['error']="No data found for the filters applied"
    return final_data_list

def graph_data(request):
    filter_args = extractFiltersFromRequest(request)

    final_data_list = {}

    sql_query = get_graphs_query(**filter_args)
    result = getPandasDataframe(sql_query)

    if filter_args['chart_name'] != 'state__#trainings':
        data_to_send = pandas_default_aggregation(filter_args['chart_name'], result)
    else:
        data_to_send = number_of_trainings(filter_args['chart_name'], result)

    return HttpResponse(json.dumps(data_to_send))
