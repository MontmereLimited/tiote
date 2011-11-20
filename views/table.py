from django.http import HttpResponse, Http404
from django.template import loader, RequestContext, Template
from django.views.decorators.http import require_http_methods

from tiote import forms, functions


def browse(request):
    # row(s) deletion request handling
    if request.method == 'POST' and request.GET.get('update') == 'delete':
        # might be needed for future corrections
#        l = request.POST.get('whereToEdit').strip().split(';');
#        conditions = functions.get_conditions(l)
        conditions = [functions.construct_cond(item[0], item[1]) 
            for item in functions.dict_conds(request.POST.get('whereToEdit')) ]
        query_data = {'database': request.GET.get('database'),'table': request.GET.get('table'),
             'conditions': conditions}
        if request.GET.get('schema'):
            query_data['schema'] = request.GET.get('schema')
        return functions.rpr_query(request, 'delete_row', query_data)
    # row(s) edit/updating request handling
    elif request.method == 'POST' and request.GET.get('update') == 'edit':
        return functions.http_500('feature not yet implemented!')
    
    return functions.response_shortcut(request)


def structure(request):
    TableForm = forms.get_dialect_form('TableForm', functions.get_conn_params(request)['dialect'])
    params = request.GET
    supported_engines = functions.common_query(request, 'supported_engines')
    charset_list = functions.common_query(request, 'charset_list')
    existing_tables = functions.rpr_query(request, 'existing_tables')
    # column deletion
    if request.method == 'POST' and request.GET.get('update'):
        l = request.POST.get('whereToEdit').strip().split(';');
        conditions = functions.get_conditions(l)
        q = ''
        if request.GET.get('update') == 'edit':
            q = 'drop_table'
            return HttpResponse('update not yet implemented!')
        elif request.GET.get('update') == 'delete':
            q = 'delete_column'
            query_data = {'db': request.GET.get('database'), 'table': request.GET.get('table'),
                          'conditions': conditions}
            
            return functions.rpr_query(request, q, query_data)
            
    # column creation
    if request.method == 'POST':
        column_count = 0
        form = TableForm(engines=supported_engines, charsets=charset_list, data=request.POST, edit=True,
            column_count=(column_count+1), existing_tables=existing_tables, column_form=True)
        if form.is_valid():
            query_data = {'column_count':(column_count+1), 'db': request.GET.get('database'),
                          'table': request.GET.get('table')}
            query_data.update(form.cleaned_data)
            return functions.rpr_query(request, 'create_column', query_data)
        else:
            return functions.response_shortcut(request, template='form_errors',
                extra_vars={'form':form,})
    else:
        form = TableForm(engines=supported_engines, charsets=charset_list, edit=True
            , label_suffix=' ->', existing_tables=existing_tables, column_form=True)
        
    return functions.response_shortcut(request, extra_vars={'form': form, 'edit':False,
        'table_fields': ['name', 'engine', 'charset', 'inherit', 'of_type'],
        'odd_fields': ['type','key','charset',]}
    )


def insert(request):
    pass


def edit(request):
    pass



def import_(request):
    pass


def export(request):
    pass

def route(request):
    if request.GET.get('view') == 'browse':
        return browse(request)
    elif request.GET.get('view') == 'structure':
        return structure(request)
    elif request.GET.get('view') == 'import':
        return import_(request)
    elif request.GET.get('view') == 'export':
        return export(request)
    else:
        return http_500('malformed URL')