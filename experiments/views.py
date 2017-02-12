from django.shortcuts import render, redirect
from django.http import HttpResponse
import json
from django.utils.safestring import mark_safe
import requests
import os
from models import *
import random
import copy
from django.forms.models import model_to_dict
from datetime import timedelta


def index(request):
    used_ids = list(Subject.objects.all().values_list('pk', flat=True).order_by('-pk'))
    if len(used_ids) != 0:
        return render(request, 'index.html', {"used_ids": used_ids})
    else:
        return render(request, 'index.html')

def index_results(request):
    return render(request, 'index.html', {"view_results":True})

def results(request, subid):
    if request.method == "POST":
        try:
            existing_user = Subject.objects.get(pk=request.POST['subid'])
            request.session['user'] = request.POST['subid']
        except:
            return redirect('/admin/experiments/subject/add')
    try:
        sub = Subject.objects.get(pk=request.session['user'])
    except:
        return HttpResponse("I couldn't find the subject you're looking for.")

    responses = Response.objects.filter(block__subject=sub)
    dict_responses = []
    for response in responses:
        if (response.given_response != None):
            temp_dict = model_to_dict(response)
            temp_dict['time'] = response.block.created
            temp_dict['phase'] = response.block.phase.phase_num
            temp_dict['stimulus'] = model_to_dict(response.stimulus)
            if response.correct_response == 1:
                temp_dict['correct'] = model_to_dict(response.option_1)
            elif response.correct_response == 2:
                temp_dict['correct'] = model_to_dict(response.option_2)
            else:
                temp_dict['correct'] = model_to_dict(response.option_3)

            if response.given_response == 1:
                temp_dict['given'] = model_to_dict(response.option_1)
            elif response.given_response == 2:
                temp_dict['given'] = model_to_dict(response.option_2)
            else:
                temp_dict['given'] = model_to_dict(response.option_3)

            dict_responses.append(temp_dict)
    sorted_responses = sorted(dict_responses, key=lambda k: k['time'])

    return render(request, 'results.html', {'responses':sorted_responses, 'sub':model_to_dict(sub)})

def session(request):
    if request.method == "POST":
        try:
            existing_user = Subject.objects.get(pk=request.POST['subid'])
            if request.POST['Action'] == "Start Session":
                if existing_user.active == False:
                    return HttpResponse("This user is no longer valid to use for trials")
                request.session['user'] = request.POST['subid']
                new_session_length = SessionLength(subject=existing_user, trials=0)
                new_session_length.save()
                request.session['session_length'] = new_session_length.pk
                return redirect('myself')
            return redirect('results', request.POST['subid'])
        except:
            return redirect('/admin/experiments/subject/add')
    else:
        if 'user' in request.session:
            try:
                return redirect(Subject.objects.get(pk=request.session['user']))
            except:
                pass
        return HttpResponse("Failure!")

def response_set(request, responseid):
    try:
        response_block = ResponseBlock.objects.get(id=responseid)
    except:
        return HttpResponse("Oops! This page is looking for a response set that hasn't been recorded.")
    responses = Response.objects.filter(block=response_block)
    return render(request, 'response_set.html', {'response_block': response_block, 'responses': responses})

def myself(request):
    if not 'user' in request.session:
        return HttpResponse("Please return to the landing page and enter a subject ID.")
    try:
        sub = Subject.objects.get(pk=request.session['user'])
    except:
        return HttpResponse("Oops! This page is looking for a subject that we don't have any info for.<br>Please return to the landing page and enter an ID.")

    return render(request, 'subject.html', {'subject': sub, 'admin': False})

def trial(request):
    if not 'user' in request.session:
        return HttpResponse("Please return to the landing page and enter a subject ID.")
    try:
        sub = Subject.objects.get(pk=request.session['user'])
    except:
        return HttpResponse("I couldn't find the subject you're looking for. Please return to the landing page and enter an ID.")

    singleSets = SingleSet.objects.filter(phases=sub.phase)
    trial = []
    for singleSet in singleSets:
        for i in range(singleSet.frequency):
            options_list = []
            options_list.append(singleSet.option_1)
            options_list.append(singleSet.option_2)
            options_list.append(singleSet.option_3)
            random.shuffle(options_list)

            temp_dict = model_to_dict(singleSet)
            temp_dict['left'] = model_to_dict(options_list[0])
            temp_dict['center'] = model_to_dict(options_list[1])
            temp_dict['right'] = model_to_dict(options_list[2])
            del temp_dict['phases']
            temp_dict['stimulus'] = model_to_dict(singleSet.stimulus)
            trial.append(temp_dict)
    random.shuffle(trial)
    new_block = ResponseBlock(subject=sub, phase=sub.phase)
    new_block.save()
    for i in range(len(trial)):
        stimulus = Symbol.objects.get(pk=trial[i]["stimulus"]["id"])
        option_1 = Symbol.objects.get(pk=trial[i]["option_1"])
        option_2 = Symbol.objects.get(pk=trial[i]["option_2"])
        option_3 = Symbol.objects.get(pk=trial[i]["option_3"])
        new_response = Response(block=new_block, stimulus=stimulus, option_1=option_1, option_2=option_2, option_3=option_3, correct_response=trial[i]["correct_response"])
        new_response.save()
        trial[i]["response_id"] = new_response.pk

    session_length = SessionLength.objects.get(pk=request.session['session_length'])
    session_length.trials += 1
    session_length.save()

    if sub.phase.id == 4:
        instructions = "In your next session, there never will be any stars or greyed out symbols. The computer still will record whether your choice is correct or not. Good Luck!"
    elif sub.phase.id == 8:
        instructions = 'This program will present many trials; each trial will present you with four symbols. One will be in the center of the screen, with three others below it. Click the mouse over any of the three symbols you think goes with the center sample item. Good luck!'
    else:
        instructions = 'This program will present many trials; each trial will present you with four symbols. One will be in the center of the screen, with three others below it. Click the mouse over any of the three symbols you think goes with the center sample item. After your selection one of two things will occur: (1) stars will appear on the screen or (2) the symbols will be greyed out. If stars appear on the screen this means you have selected the correct response. If the symbols are greyed out this means you have selected incorrectly. Good luck!'

    return render(request, 'trial.html', {'trial': mark_safe(json.dumps(trial)), 'feedback': sub.phase.feedback, 'instructions': instructions})

def report_results(request):
    if request.method != "POST":
        return HttpResponse("You have reached this page in error. If you want to begin a trial, return to the subject view page.")
    block = ""
    json_object = json.loads(request.body)
    if len(json_object) < int(json_object['trial_length']) + 1:
        try:
            db_response = Response.objects.get(id=json_object[0].response_id)
            block = db_response.block
            block.delete()
        except:
            print "Delete failed"
        return redirect("/myself")
    for response in json_object:
        try:
            db_response = Response.objects.get(id=json_object[response]['response_id'])
            db_response.response_time = timedelta(milliseconds=json_object[response]['response_time'])
            db_response.given_response = json_object[response]['given_response']
            db_response.save()
            if block == "":
                block = db_response.block
        except:
            pass

    if block != "":
        if block.successful() == "Passed":
            sub = block.subject
            failures = Failure.objects.filter(subject=sub, phase=sub.phase)
            for fail in failures:
                fail.times_failed = 0
                fail.save()
            phases = Phase.objects.filter(group=sub.group).order_by('ordering')
            for phase in phases:
                if phase.ordering > sub.phase.ordering:
                    old_phase = sub.phase
                    sub.phase = phase
                    sub.save()
                    return HttpResponse("You have passed Phase %s! You may now continue on to Phase %s when you are ready." % (old_phase.phase_num, sub.phase.phase_num))
            sub.active = False
            sub.save()
            return HttpResponse("Thank you for your participation! You will receive an email with further information by tomorrow evening.")
        else:
            sub = block.subject
            if sub.phase.fail_limit > 0:
                old_failures = Failure.objects.filter(subject=sub, phase=sub.phase)
                if len(old_failures) > 0:
                    fail = old_failures[0]
                else:
                    fail = Failure(subject=sub, phase=sub.phase, times_failed=0)
                    fail.save()
                fail.times_failed += 1
                fail.save()
                if fail.times_failed >= sub.phase.disable_fail_limit:
                    sub.active = False
                    sub.save()
                    return HttpResponse("Thank you for your participation! You will receive an email with further information by tomorrow evening.")
                elif fail.times_failed == sub.phase.disable_fail_limit/sub.phase.fail_limit:
                    old_phase = sub.phase
                    sub.phase = sub.phase.fail_phase
                    sub.save()
                    return HttpResponse("You have not yet mastered Phase %s. You may return to Phase %s when you are ready for further training." % (old_phase.phase_num, sub.phase.phase_num))
            return HttpResponse("You have not yet mastered Phase %s. You may try again whenever you are ready." % sub.phase.phase_num)
