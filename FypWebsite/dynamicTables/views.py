from django.shortcuts import render,redirect
from .models import ModelDefinition,step_tracker,Data
from .forms import tableCreation,FieldCreation,DataString,DataInt,DataFloat
from django.http import JsonResponse
from django.template.defaultfilters import slugify
from django.contrib.auth.decorators import login_required
# Create your views here.


def data_validate(data,f_dict):
    #print(f_dict)
    required_in=f_dict["required"]
    if f_dict['data_type'].lower() == 'string':
        if len(data)>f_dict['max_length']:
            return False
        sd=DataString(required_in=required_in,data={'stringField':data})
        if sd.is_valid():
            return True
    elif f_dict['data_type'].lower() == 'integer':
        if data=="" and (not required_in):
            return True
        try:
            data=int(data)
        except:
            return False
        id=DataInt(required_in=required_in,data={'intField':data})
        if id.is_valid():
            return True
    elif f_dict['data_type'].lower() == 'float':
        if data=="" and (not required_in):
            return True
        try:
            data=float(data)
        except:
            return False
        fd=DataFloat(required_in=required_in,data={'floatField':data})
        if fd.is_valid():
            return True
    else:
        return False
    return False


@login_required(login_url="/login/")
def tablesPage(request):
    context={'active_view':'tables'}
    template_name="dynamicTables/tablelist.html"
    context['content_dicts']=[]
    tables=ModelDefinition.objects.all()
    for tab in tables:
        column_list=[]
        for c in tab.definition['fields']:
            column_list.append(
            {
            'name':c['verbose_name'],
            'd_type':c['data_type'],
            'max_length':(c['max_length'] if c['data_type'].lower()=='string' else ""),
            'required':c['required']
            }
            )
        context['content_dicts'].append({
        "title":tab.verbose_name,
        "table_group":tab.table_group,
        "columns":column_list,
        "user":tab.user,
        "view_data":"/tables/"+tab.name+"/"
        })

    context['content_template_name']="dynamicTables/tableListInner.html"
    context['create_url']="/tables/create/"
    return render(request,template_name,context)
@login_required(login_url="/login/")
def createTable(request):
    context={'active_view':'tables'}
    template_name="dynamicTables/createTable.html"
    if request.is_ajax():
        if request.POST.get('ajax_type')=="add_field":
            s=step_tracker.objects.get(pk=request.session['id'])
            s.step=s.step+1
            s.save()
            field_count=s.step
            field_form=FieldCreation(auto_id=False)
            with open("templates/card_container.html","r") as f:
                container=f.read()
            with open("templates/card_inner.html","r") as f:
                inner=f.read()
            replace_list=[("{% include content_template_name with fed_data=content_dict %}",inner),
                          ("{%block title%}{%endblock%}","Column "+str(field_count)),
                          ("{%block main_body%}{%endblock%}","<div class='form-group table-field-container-"+str(field_count)+"'>"+field_form.as_p()+"</div>"),
                          ("{%block second_body%}{%endblock%}",""),
                          ("{%block footer%}{%endblock%}","")]
            for replace_tuple in replace_list:
                container=container.replace(replace_tuple[0],replace_tuple[1])
            return JsonResponse({"add_field_form":container},status=200)
        elif request.POST.get('ajax_type')=="post_table":
            table_name=request.POST.get('ajax_name')
            table_group=request.POST.get('ajax_group')
            names=request.POST.getlist('names[]')
            data_types=request.POST.getlist('data_types[]')
            max_lengths=request.POST.getlist('max_lengths[]')
            requireds=request.POST.getlist('requireds[]')
            requireds=[(True if i=="true" else False) for i in requireds]
            form_list=[]
            nums_list=[i+1 for i in range(len(names))]
            alert="success"
            for name, d_type, m_len, required in zip(names,data_types,max_lengths,requireds):
                field_f=FieldCreation(auto_id=False,data={
                'name':name
                ,'data_type':d_type
                ,'max_length':m_len
                ,'required':required
                })
                if not field_f.is_valid():
                    alert='false'
                form_list.append(field_f.as_p())
            t_form=tableCreation(data={'table_group':table_group,'verbose_name':table_name})
            if not t_form.is_valid():
                alert='false'
            if alert=='success':
                verbose_name = table_name
                definition = {"fields": [],"global_options": {"guest": {"verbose_name": "Allow guests to enter data","option": True},
                  "public": {"verbose_name": "Data is publicly accessible","option": False}}}
                types=[(0,"String"),(1,"Integer"),(2,"Float")]
                for name, d_type, m_len, required in zip(names,data_types,max_lengths,requireds):
                    data={
                      "name": slugify(name),
                      "verbose_name": name,
                      "data_type": types[int(d_type)][1],
                      "required": required,
                    }
                    if (types[int(d_type)][1]).lower()=='string':
                        data["max_length"]=int(m_len)
                    definition['fields'].append(data)
                mod_def=ModelDefinition(**{
                'user':request.user,
                'verbose_name' : table_name,
                'table_group':table_group,
                'definition':definition
                })
                mod_def.save()
                s=step_tracker.objects.get(pk=request.session['id'])
                s.delete()
                return JsonResponse({'redirect':request.build_absolute_uri('/tables/'+slugify(table_name)+'/'),"field_nums":nums_list,"forms":form_list,'table_form':t_form.as_p()},status=200)
            #REdirect to table view page
            return JsonResponse({"field_nums":nums_list,"forms":form_list,'table_form':t_form.as_p()},status=200)
    new_step=step_tracker.objects.create(step=0)
    new_step.save()
    request.session.__setitem__('id', new_step.pk)
    table_form=tableCreation()
    context['content_template_name']="dynamicTables/tableCreateCard.html"
    context['content_dicts']=[]
    context['content_dicts'].append({"title":"Create Table",
                            "form":table_form,
                            "user":request.user,
                            "completion_url":"fqefqd"})
    context['form_table']=table_form
    return render(request,template_name,context)
@login_required(login_url="/login/")
def viewTable(request,view_slug):
    context={"active_view":"tables","donwload_name":view_slug}
    template_name="dynamicTables/tableView.html"
    table=ModelDefinition.objects.get(name=view_slug)
    datas=Data.objects.filter(model_definition=table)
    if request.user==table.user:
        context['creator']=True
    rows=[]
    fields=[t['name'] for t in table.definition['fields']]
    types=[t['data_type'] for t in table.definition['fields']]
    requireds=[("Required" if t['required'] else "") for t in table.definition['fields']]
    max_lengths=[('<'+str(t['max_length']) if 'max_length' in [*t.keys()] else "") for t in table.definition['fields']]
    for data in datas:
        data_dict={}
        for field in fields:
            if field in list(data.data.keys()):
                data_dict[field]=data.data[field]
        rows.append(data_dict)
    context['rows']=rows
    context["columns"]=fields
    context["types"]=types
    context["requireds"]=requireds
    context["max_lengths"]=max_lengths
    if request.is_ajax():
        if request.POST.get('ajax_type')=="add_row":
            if request.user==table.user:
                status="success"
                row=request.POST.getlist('row_data[]')
                field_def=table.definition['fields']
                data_dict={}
                valid=True
                for data,col in zip(row,fields):
                    print(data,col)
                    for f_dict in field_def:
                        if slugify(col) == f_dict["name"]:
                            if data_validate(data,f_dict):
                                if f_dict['data_type']=="integer":
                                    val=(int(data) if data!="" else None)
                                elif f_dict['data_type']=="float":
                                    val=(float(data) if data!="" else None)
                                else:
                                    val=data
                                data_dict[f_dict["name"]]=val
                            else:
                                valid=False
                print(row,data_dict,valid)
                if valid:
                    try:
                        d_obj=Data.objects.create(model_definition=table,data=data_dict)
                        d_obj.save()
                    except:
                        status='fail'
                else:
                    status="fail"
                return JsonResponse({"status":status,"columns":fields,"row":list(data_dict.values())},status=200)
    return render(request,template_name,context)
