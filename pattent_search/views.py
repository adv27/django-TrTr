import json

from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect
import xmltodict

from pattent_search.models import Patent
from pattent_search.utils import get_values_recursive
from django.contrib.messages import get_messages
import os

import time

def index(request):
    context = {
        'messages': get_messages(request)
    }
    return render(request,context=context,template_name='index.html')

def show(request,pat_id):
    context = {
        'patten': Patent.objects.filter(id=pat_id).first(),
        'time': 123
    }
    return render(request, context=context, template_name='show.html')

def listing(request):
    t0 = time.time()
    query = request.GET.get('q')
    if query:
        pattens = Patent.objects.search_text(query).order_by('$text_score')
    else:
        pattens = Patent.objects
    
    page = request.GET.get('page', 1)
    
    paginator = Paginator(pattens, 10)
    try:
        pattens = paginator.page(page)
    except PageNotAnInteger:
        pattens = paginator.page(1)
    except EmptyPage:
        pattens = paginator.page(paginator.num_pages)
    
    context = {
        'pattens' :pattens,
        'time'    :time.time()-t0
    }
    return render(request,context=context,template_name='listing.html')


def upload_file(request):
    
    file = request.FILES.getlist('upload_file')
    _dir = request.POST.get('upload_dir')

    if dir and not file:
        for filename in os.listdir(_dir):

            if not filename.lower().endswith('.xml') or ' ' in filename or Patent.objects.filter(filename=filename).first():
                continue

            f = open(_dir+filename)

            try:
                doc = json.loads(json.dumps(xmltodict.parse(f.read())))
                f.close()
                store_xml(filename, doc)
            except Exception as e:
                f.close()
                continue
            messages.success(request, 'Done')
        return redirect('/')

    
    
    if (not file or len(file) == 0) :
        return redirect('/')
    print('len(file)')
    print(len(file))
    
    skiped_file = []
    for idx,f in enumerate(file):
        print('%d/%d completed'% (idx+1,len(file)))
        
        filename = f.name.split('/')[-1]
        
        if Patent.objects.filter(filename=filename).first():
            skiped_file.append(filename)
            print('Skip file duplicate')
        
        doc = json.loads(json.dumps(xmltodict.parse(f.read())))
        f.close()
        try:
            store_xml(filename,doc)
        except Exception as e :
            skiped_file.append(filename)
            print('Skip')
            print(e)
            continue
    
    messages.success(request,'Complete upload %d files' % (len(file)-len(skiped_file)))
    if len(skiped_file) > 0:
        if len(skiped_file) > 10:
            messages.error(request, 'File format error or duplicate ! skip %d files : [...]' % len(skiped_file) )
        else:
            messages.error(request, 'File format error or duplicate ! skip %d files: %s' % (len(skiped_file),' , '.join(skiped_file)))
    
    return redirect('/')


def store_xml(filename,content):
    print(content)

    doc = json.loads(json.dumps(xmltodict.parse(content)))
    title = doc['patent-application-publication'] \
        ['subdoc-bibliographic-information'] \
        ['technical-information'] \
        ['title-of-invention']
    
    abstract = doc['patent-application-publication'] \
        ['subdoc-abstract'] \
        ['paragraph']
    if isinstance(abstract, list):
        abstract = get_values_recursive(abstract)
    else:
        abstract = abstract['#text']
    
    summary = doc['patent-application-publication'] \
        ['subdoc-description'] \
        ['summary-of-invention'] \
        ['section']
    
    detail = doc['patent-application-publication'] \
        ['subdoc-description'] \
        ['detailed-description'] \
        ['section']
    
    detail_txt = get_values_recursive(detail)
    summary_txt = get_values_recursive(summary)
    
    pat = Patent(
        filename=filename,
        title=title,
        abstract=abstract,
        content=summary_txt + '\n' + detail_txt,
    )
    pat.save()

