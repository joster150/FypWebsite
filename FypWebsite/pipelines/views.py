from django.shortcuts import render,redirect
from .forms import PipelineCreateSubmit,PipelineCreateStep,Variable,TableParam,TextInput,BooleanInput,IntInput,FloatInput,Include_Output,FileInput,FilesInput
from .models import Pipeline,PipelineStep
from notebooks.models import NotebookModel
from dynamicTables.models import step_tracker,ModelDefinition,Data
from django.http import JsonResponse
from django.template.defaultfilters import slugify
import sys,os,json
from importnb import Notebook
from importlib import reload,import_module
from django.conf import settings
import pandas as pd
from django.contrib.auth.decorators import login_required
dir = settings.SCRIPTS_ROOT
# Create your views here.
@login_required(login_url="/login/")
def pipelinesPage(request):
    context={'active_view':'pipelines'}
    template_name="pipelines/pipelinelist.html"
    context['content_template_name']="pipelines/linelistcard.html"
    context['content_dicts']=[]
    pipes=Pipeline.objects.all()
    if pipes.exists():
        for pipe in pipes:
            context['content_dicts'].append({"title":pipe.title,
                                "description":pipe.description,
                                "user":pipe.user,
                                "slug":pipe.slug
                                })
    return render(request,template_name,context)
@login_required(login_url="/login/")
def createPipeline(request):
    context={'active_view':'pipelines'}
    template_name="pipelines/createPipeline.html"
    modules=NotebookModel.objects.all()
    if modules.exists():
        mod_choices=tuple([(i,mod.name) for i,mod in enumerate(modules)])
        choices=tuple([(i,key) for i,key in enumerate(modules[0].functions.keys())])
        if request.is_ajax():
            if request.POST.get('ajax_type')=="add_step":
                s=step_tracker.objects.get(pk=request.session['id'])
                s.step=s.step+1
                step_count=s.step
                form=PipelineCreateStep(mod_choices_param=mod_choices,choices_param=choices)
                with open("templates/card_container.html","r") as f:
                    container=f.read()
                with open("templates/card_inner.html","r") as f:
                    inner=f.read()
                replace_list=[("{% include content_template_name with fed_data=content_dict %}",inner),
                              ("{%block title%}{%endblock%}","Step "+str(step_count)),
                              ("{%block main_body%}{%endblock%}","<div id='Step "+str(step_count)+"' class='form-group step ajax-form-step-"+str(step_count)+"'>"+form.as_p()+"</div>"),
                              ("{%block second_body%}{%endblock%}",""),
                              ("{%block footer%}{%endblock%}","")]
                for replace_tuple in replace_list:
                    container=container.replace(replace_tuple[0],replace_tuple[1])
                s.save()
                return JsonResponse({"form":container},status=200)
            elif request.POST.get('ajax_type')=="post_pipe":
                title=request.POST.get('ajax_title')
                description=request.POST.get('ajax_description')
                descriptions=request.POST.getlist('descriptions[]')
                using_modules=request.POST.getlist('using_modules[]')
                using_functions=request.POST.getlist('using_functions[]')
                outputs=request.POST.getlist('outputs[]')
                step_nums=request.POST.getlist('step_nums[]')
                step_nums_int=[int(i[i.index(" "):]) for i in step_nums]
                forms=[]
                alert="success"
                if len(step_nums)==0:
                    alert="At least one step should be added"
                pipeline_form=PipelineCreateSubmit(data={'description':description,'title':title})
                if not pipeline_form.is_valid():
                    alert='Invalid Pipeline Information'
                for a,b,c,d,e in zip(descriptions,using_modules,using_functions,outputs,step_nums_int):
                    choices=tuple([(i,key) for i,key in enumerate(modules[int(b)].functions.keys())])
                    form=PipelineCreateStep(data={'using_module':b,'using_function':c,
                                        'description':a,'output':d},mod_choices_param=mod_choices,choices_param=choices)

                    forms.append(form.as_p())
                    if not form.is_valid():
                        alert='Invalid Pipeline Step'
                if alert=='success':
                    if Pipeline.objects.filter(slug=slugify(pipeline_form.cleaned_data['title'])).exists():
                        alert='Pipeline with this name already exists'
                    else:
                        new_pipe=Pipeline.objects.create(user=request.user,title=pipeline_form.cleaned_data['title'],
                        slug=slugify(pipeline_form.cleaned_data['title']),description=pipeline_form.cleaned_data['description'])
                        for a,b,c,d,e in zip(descriptions,using_modules,using_functions,outputs,step_nums_int):
                            choices=tuple([(i,key) for i,key in enumerate(modules[int(b)].functions.keys())])
                            form=PipelineCreateStep(data={'using_module':b,'using_function':c,
                                                'description':a,'output':d},mod_choices_param=mod_choices,choices_param=choices)
                            if form.is_valid():
                                mod=NotebookModel.objects.filter(name=mod_choices[int(b)][1])
                                print(mod_choices[int(b)][1])
                                if mod.exists():
                                    new_step=PipelineStep.objects.create(pipeline_id=new_pipe,step_num=e,
                                    module=mod[0],function=choices[int(c)][1],
                                    description=form.cleaned_data['description'], output=form.cleaned_data['output'])
                        return JsonResponse({'redirect':request.build_absolute_uri('/pipelines/'+new_pipe.slug+'/'),'step_nums':step_nums_int,"forms":forms,'status':alert,'pipe_form':pipeline_form.as_p()},status=200)

                return JsonResponse({'step_nums':step_nums_int,"forms":forms,'status':alert,'pipe_form':pipeline_form.as_p()},status=200)
            elif request.POST.get('ajax_type')=="select_modules":
                using_module=request.POST.get('ajax_module')
                step=request.POST.get('ajax_step')
                step=int(step[step.index(" "):])
                options=''
                for i,key in enumerate(modules[int(using_module)].functions.keys()):
                    options+='<option value="'+str(i)+'">'+key+'</option>'
                return JsonResponse({'step_num':step,'options':options},status=200)
        #elif request.method == 'POST':
                # submit_form = PipelineCreateSubmit(request.POST)
                # if submit_form.is_valid():
                #     title=request.POST.get('title')
                #     slug=slugify(title)
                #     print(slug)
                #     return redirect('/pipelines/use/'+slug+'/')
        new_step=step_tracker.objects.create(step=0)
        new_step.save()
        request.session.__setitem__('id', new_step.pk)
        submit_form=PipelineCreateSubmit()
        context['content_template_name']="pipelines/createPipeCard.html"
        context['content_dicts']=[{"title":"Create Pipeline",
                                "form":submit_form,
                                "user":request.user,
                                }]
    return render(request,template_name,context)
@login_required(login_url="/login/")
def viewPipeline(request,pipe_slug):
    context={'active_view':'pipelines'}
    template_name="pipelines/viewPipeline.html"
    form_dict={'file_browse':FileInput,'files_browse':FilesInput,'variable':Variable,'choice':Variable,
                'text_input':TextInput,'float_input':FloatInput,'int_input':IntInput,'table_param':TableParam,'boolean':BooleanInput}

    nb_script_groups=NotebookModel.objects.values_list('notebook_group',flat=True).distinct()
    notebooks=NotebookModel.objects.all()
    imported_notebooks={}
    if notebooks.exists():
        for fldr in nb_script_groups:
            sys.path.append(os.path.join(dir,fldr.upper()))
        for nb in notebooks:
            path,tail=os.path.split(nb.notebook.path)
            tail=tail[:tail.index(".")]
            if tail not in sys.modules:
                with Notebook():
                    module_temp=import_module(tail)
                    imported_notebooks[nb.name]=module_temp
                    #print(imported_notebooks)
            else:
                imported_notebooks[nb.name]=i = __import__(tail, fromlist=[''])
    pipe=Pipeline.objects.get(slug=pipe_slug)
    pipe_steps=PipelineStep.objects.filter(pipeline_id=pipe.pk)
    step_dicts=[]
    pre_pre_form='<div><h6 class="text-muted my-0 toggle">Param '
    pre_form=' \/</h6><div class="my-1" style="display:none">'
    post_form='</div></div>'
    pipeline_valid=True
    pipeline_out={}
    outputs={}
    out_choices_list=[]
    context['content_dicts1']={"name":pipe.title}
    tables=ModelDefinition.objects.all()
    table_groups=[*set([t.table_group for t in tables])]
    unique_table_groups=[(i,t_group) for i,t_group in enumerate(table_groups)]
    table_group_form=Variable(choices_param=unique_table_groups)
    context['content_dicts1']['table_groups']=table_group_form.as_p().replace('<label for="id_form_val">Form val:</label>','').replace('ajax-using_functions','table_group')
    tables_in_group=[(i,t.name) for i,t in enumerate(tables) if t.table_group == unique_table_groups[0][1]]
    tables_in_group_form=Variable(choices_param=tables_in_group)
    context['content_dicts1']['tables_in_group']=tables_in_group_form.as_p().replace('<label for="id_form_val">Form val:</label>','').replace('ajax-using_functions','table_select')
    columns_in_table=[(i,f['name']) for i,f in enumerate(ModelDefinition.objects.get(name=tables_in_group[0][1]).definition["fields"])]
    columns_form=Variable(choices_param=columns_in_table)
    context['content_dicts1']['columns_in_table']=columns_form.as_p().replace('<label for="id_form_val">Form val:</label>','').replace('ajax-using_functions','search_column')

    datas=Data.objects.filter(model_definition=ModelDefinition.objects.get(name=tables_in_group[0][1]))
    rows=[]
    fields=[t['name'] for t in ModelDefinition.objects.get(name=tables_in_group[0][1]).definition['fields']]
    for data in datas:
        data_dict={}
        for field in fields:
            if field in list(data.data.keys()):
                data_dict[field]=data.data[field]
        rows.append(data_dict)
    context['content_dicts1']['rows']=rows
    context['content_dicts1']['table_data_columns']=fields
    #context['content_dicts1']=[context['content_dicts1']]
    context['content_template_name1']="pipelines/FirstTableCard.html"


    if request.is_ajax():
        if request.POST.get('ajax_type')=="table_select":
            table=request.POST.get('ajax_table')
            table=ModelDefinition.objects.get(name=table)
            datas=Data.objects.filter(model_definition=table)
            rows=[]
            fields=[t['name'] for t in table.definition['fields']]
            for data in datas:
                data_dict={}
                for field in fields:
                    if field in list(data.data.keys()):
                        data_dict[field]=data.data[field]
                rows.append(data_dict)
            table_head_str=""
            table_body_str=""
            for field in fields:
                table_head_str+='<th scope="col">'+field+'</th>'
            search_cols=Variable(choices_param=[(i,f) for i,f in enumerate(fields)])
            search_cols=search_cols.as_p().replace('<label for="id_form_val">Form val:</label>','').replace('ajax-using_functions','search_column')
            print(fields,rows,search_cols)
            for row in rows:
                table_body_str+="<tr>"
                for field in fields:
                    table_body_str+="<td>"+str(row[field])+"</td>"
                table_body_str+="</tr>"
            return JsonResponse({'table_body':table_body_str,"table_head":table_head_str,"search_cols":search_cols},status=200)
        elif request.POST.get('ajax_type')=='table_group_choice':
            table_group=request.POST.get('ajax_table_group')
            tables_in_group=[(i,t.name) for i,t in enumerate(tables) if t.table_group == table_group]
            tables_in_group_form=Variable(choices_param=tables_in_group).as_p().replace('<label for="id_form_val">Form val:</label>',
            '').replace('ajax-using_functions','table_select')
            columns_in_table=[(i,f['name']) for i,f in enumerate(ModelDefinition.objects.get(name=tables_in_group[0][1]).definition["fields"])]
            columns_form=Variable(choices_param=columns_in_table).as_p().replace('<label for="id_form_val">Form val:</label>',
            '').replace('ajax-using_functions','search_column')
            rows=[]
            fields=[t['name'] for t in ModelDefinition.objects.get(name=tables_in_group[0][1]).definition['fields']]
            datas=Data.objects.filter(model_definition=ModelDefinition.objects.get(name=tables_in_group[0][1]))
            for data in datas:
                data_dict={}
                for field in fields:
                    if field in list(data.data.keys()):
                        data_dict[field]=data.data[field]
                rows.append(data_dict)
            table_head_str=""
            table_body_str=""
            for field in fields:
                table_head_str+='<th scope="col">'+field+'</th>'
            search_cols=Variable(choices_param=[(i,f) for i,f in enumerate(fields)])
            search_cols=search_cols.as_p().replace('<label for="id_form_val">Form val:</label>','').replace('ajax-using_functions','search_column')
            print(fields,rows,search_cols)
            for row in rows:
                table_body_str+="<tr>"
                for field in fields:
                    table_body_str+="<td>"+str(row[field])+"</td>"
                table_body_str+="</tr>"
            return JsonResponse({'table_body':table_body_str,"table_head":table_head_str,'tables_in_group':tables_in_group_form,"search_cols":columns_form},status=200)


    step_output_names=[]
    for step_iter,step in enumerate(pipe_steps):
        input_dict=imported_notebooks[step.module.name].in_out_def()[step.function]['inputs']
        output_dict=imported_notebooks[step.module.name].in_out_def()[step.function]['outputs']
        input_form_part=""
        outputs[step.step_num]=[step.module.name,step.function,step.output]
        pipeline_out[step.step_num]={}
        print(request.FILES)

        replace_name_include_outputs=str(step.step_num)+'_'+step.module.name+'_'+'include_output'
        step_output_names.append(replace_name_include_outputs)
        if request.method == 'POST':
            inc_out_form=Include_Output(data={"include_output":request.POST.get(replace_name_include_outputs)}).as_p().replace('name="include_output"','name="'+replace_name_include_outputs+'"')
        else:
            if step_iter+1==len(pipe_steps):
                inc_out_form=Include_Output(data={"include_output":'on'}).as_p().replace('name="include_output"','name="'+replace_name_include_outputs+'"')
            else:
                inc_out_form=Include_Output().as_p().replace('name="include_output"','name="'+replace_name_include_outputs+'"')
        for param,type2 in input_dict.items():
            input_var=str()
            replace_name=str(step.step_num)+'_'+step.module.name+'_'+step.function+'_'+param+'_'+type2
            if replace_name in list(request.FILES.keys()):
                #print(type2)
                if type2=="files_browse":
                    pipeline_out[step.step_num][param]='FILES'+replace_name
                else:
                    pipeline_out[step.step_num][param]='FILE'+replace_name
            if type2 == "table_param":
                form=form_dict[type2](choices_param=[])
            elif 'choice' in type2:
                choicelist=type2[type2.index("[")+1:type2.index("]")].split(',')
                #print(choicelist)
                choicetuplelist=[(i,val) for i,val in enumerate(choicelist)]
                form=form_dict['choice'](choices_param=choicetuplelist)
            elif type2 != "variable":
                form=form_dict[type2]()
            else:
                out_choices_tuple=tuple(out_choices_list)
                form=form_dict[type2](choices_param=out_choices_tuple)

            if request.method == 'POST' and type2 not in ['file_browse','files_browse']:
                input_var=request.POST.get(replace_name)
                if type2 not in ['files_browse']:
                    if type2 == "table_param":
                        tuple_param=str(input_var)[str(input_var).index('--')+2:]
                        out_choices_list_2=[(input_var,tuple_param)]
                        out_choices_tuple_2=tuple(out_choices_list_2)
                        form=form_dict[type2](data={'form_val':input_var},choices_param=out_choices_tuple_2)
                    elif 'choice' in type2:
                        choicelist=type2[type2.index("[")+1:type2.index("]")].split(',')
                        #print(choicelist)
                        choicetuplelist=[(i,val) for i,val in enumerate(choicelist)]
                        form=form_dict['choice'](data={'form_val':input_var},choices_param=choicetuplelist)
                    elif type2 != "variable":
                        form=form_dict[type2](data={'form_val':input_var})
                    else:
                        out_choices_tuple=tuple(out_choices_list)
                        form=form_dict[type2](data={'form_val':input_var},choices_param=out_choices_tuple)

                    if form.is_valid():
                        if type2 == "variable":
                            pipeline_out[step.step_num][param]=out_choices_tuple[int(form.cleaned_data['form_val'])][1]
                        elif 'choice' in type2:
                            pipeline_out[step.step_num][param]=choicetuplelist[int(form.cleaned_data['form_val'])][1]
                        elif type2 == "table_param":
                            pipeline_out[step.step_num][param]=tuple_param[tuple_param.index('//')+2:]
                        else:
                            pipeline_out[step.step_num][param]=form.cleaned_data['form_val']

                    else:
                        pipeline_valid=False

            input_form_part+=pre_pre_form+param+pre_form+form.as_p().replace('<label for="id_form_val">Form val:</label>','').replace('name="form_val"','name="'+replace_name+'"')+post_form
        for name_out,typ_out in output_dict.items():
            if typ_out =="variable" or typ_out=='graph':
                out_choices_list.append((len(out_choices_list),step.output+'_out/var_'+name_out))
        step_dicts.append({'form':input_form_part,'include_output':inc_out_form,'output':step.output,'module_function':step.module.name+'/'+step.function,'description':step.description,'step_class_title':str(step.step_num).replace(" ","")})
    #print(pipeline_out)

    context['content_template_name']="pipelines/usePipeStep.html"
    context['content_dicts']=step_dicts
    #print(step_dicts)
    if request.method == 'POST' and pipeline_valid:
        context2={}
        context2['graphs']=[]
        context2['graphs2']=[]
        context2["vars"]=[]
        context2['table_var']=[]
        context2['active']=[]
        context2['graph']=[]
        context2['table']=[]
        context2["variable"]=[]
        context["out_zip"]=""
        graph_names=[]
        table_names=[]
        output_vals={}
        #print(pipeline_out)
        #include_outputs=[]
        for s_num in range(len(pipe_steps)):
            #include_outputs.append(request.POST.get(step_output_names[s_num]))
            for name,val in pipeline_out[s_num+1].items():
                if type(val) in [type(True), int, float]:
                    pass
                elif "_out/var_" in val:
                    out_name=val[val.index("_out/var_"):].replace("_out/var_","")
                    out_prefix=val[:val.index("_out/var_")]
                    step_to_use=0
                    #outputs[step.step_num]=[step.module,step.function,step.output]
                    for step_number,li in outputs.items():
                        if li[2]==out_prefix:
                            #print('found step')
                            step_to_use=step_number
                    pipeline_out[s_num+1][name]=output_vals[outputs[step_to_use][2]]['values'][out_name]
                elif "FILES" in val:
                    pipeline_out[s_num+1][name]=request.FILES.getlist(val[val.index("FILES")+5:])
                elif "FILE" in val:
                    pipeline_out[s_num+1][name]=request.FILES[val[val.index("FILE")+4:]]
            out_func=getattr(imported_notebooks[outputs[s_num+1][0]], outputs[s_num+1][1])
            output_vals[outputs[s_num+1][2]]={"types":imported_notebooks[outputs[s_num+1][0]].in_out_def()[outputs[s_num+1][1]]['outputs'],
                                            "values":out_func(**pipeline_out[s_num+1])}
            out_types_vars=output_vals[outputs[s_num+1][2]]["types"].items()
            if request.POST.get(step_output_names[s_num])=='on':#s_num+1 == len(pipe_steps):
                #print("Hello")
                for name,typ in out_types_vars:
                    context2['graph'].append(False)
                    context2['table'].append(False)
                    context2["variable"].append(False)
                    context2['active'].append(True)
                    graph_names.append("")
                    table_names.append("")
                    context2['graphs'].append("")
                    context2['table_var'].append("")
                    context2["vars"].append("")
                    context2['graphs2'].append("")
                    if typ=="graph":
                        context2['graph'][-1]=True
                        graph_names[-1]=name
                        context2['graphs'][-1]=json.dumps(output_vals[outputs[s_num+1][2]]["values"][name])
                        #print(context['graphs'])
                    elif typ=="variable":
                        out_var=output_vals[outputs[s_num+1][2]]["values"][name]
                        if isinstance(out_var,pd.DataFrame):
                            context2['table'][-1]=True
                            table_names[-1]=name
                            context2['table_var'][-1]={
                            'cols':[*out_var.columns],
                            'rows':[out_var.iloc[i,:].to_list() for i in range(len(out_var.index))]
                            }
                            #print([out_var.iloc[i,:].to_list() for i in range(len(out_var.index))])
                        else:
                            context2["variable"][-1]=True
                            context2["vars"][-1]={
                            "value":str(out_var),
                            "name":name}
                    else:
                        context2["active"][-1]=False
        context2['table_var']=zip(context2['table_var'],table_names)
        context['graphs']=[gr for gr in context2['graphs'] if gr!=""]
        context["out_zip"]=zip(context2["active"],context2["table"],context2["table_var"],context2["variable"],context2["vars"],context2["graph"],context2["graphs"],graph_names)
        #print(*context["out_zip"])
    return render(request,template_name,context)
