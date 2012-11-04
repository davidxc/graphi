# -*- coding: utf-8 -*-

"""
Author: David Wong <davidwong.xc@gmail.com>
License: 3 clause BSD license

This module mostly has view functions that return http responses.

"""

import pstats

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import simplejson
from django.core.mail import send_mail

from jsonwriters import PstatsWriter
from forms import MessageForm


def home(request):
    return render_to_response('home.html', context_instance = RequestContext(request))

def parsepython(request):
    agreement = request.POST.getlist('termsacceptance')
    if 'termsacceptance' not in agreement:
        #Check if user accepted the terms of service
        warning = {'error': 'error_terms'}
        json_warning = simplejson.dumps(warning)
        return HttpResponse(json_warning, mimetype="application/json", status=200)
    
    profile_file = request.FILES["profile"]
    if len(profile_file.name) > 30:
        #File name was too long.
        warning = {'error': 'error_length'}
        json_warning = simplejson.dumps(warning)
        return HttpResponse(json_warning, mimetype="application/json", status=200) 
         
    #File needs to be saved because load_stats in pstats.Stats takes a file name 
    #For security, Apache's LimitRequestBody is set to limit file upload size.
    path = default_storage.save("/home/david/Dropbox/personalprojects/graphi_project/graphi_project/fileuploads/", ContentFile(profile_file.read()))
    try:
        p = pstats.Stats(path)
    except:
        #Uploaded file was not valid cProfile output.
        warning = {'error': 'error_output'}
        json_warning = simplejson.dumps(warning)
        return HttpResponse(json_warning, mimetype="application/json", status=200)
     
    #Validation tests pass. Parse the file and create a json graph with PstatsWriter
    p = PstatsWriter(path)
    p.create_nodes_edges_list()
    p.create_graph()
    
    json_graph = simplejson.dumps(p.graph) 
    return HttpResponse(json_graph, mimetype="application/json", status=200)

def parsepython_example(request):
    
    #This returns the json for the example on the home page.
    
    path = "/home/david/Dropbox/personalprojects/graphi_project/graphi_main/output"
    p = PstatsWriter(path)
    p.create_nodes_edges_list()
    p.create_graph()
    
    json_graph = simplejson.dumps(p.graph) 
    
    return HttpResponse(json_graph, mimetype="application/json", status=200)

def graphing(request):
    return render_to_response('graphing.html', context_instance = RequestContext(request))

def about(request):
    return render_to_response('about.html', context_instance = RequestContext(request))


def contact(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            sender_email = form.cleaned_data['sender_email']
            subject = "Graphi Message"
            message = ' '.join([name, form.cleaned_data['message']])
            recipients = ['davidwong.xc@gmail.com']
            #send_mail does not allow newlines, so it protects against spam programs
            send_mail(subject, message, sender_email, recipients, fail_silently=True)
            return HttpResponseRedirect('/thanks/')
    else:
        form = MessageForm()
    return render_to_response('contact.html', {'form': form}, context_instance = RequestContext(request))

def thanks(request):
    return render_to_response('thanks.html', context_instance = RequestContext(request))

def hire_me(request):
    return render_to_response('hireme.html', context_instance = RequestContext(request))

def faq(request):
    return render_to_response('faq.html', context_instance = RequestContext(request))

def features(request):
    return render_to_response('features.html', context_instance = RequestContext(request))

def terms(request):
    return render_to_response('termsofservice.html', context_instance = RequestContext(request))
 


    