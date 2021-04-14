$(document).ready(function(){
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
$(document).on('click',".addCard",function(){
    $.ajax({
      url: '',
      type: 'post',
      data:{
        ajax_type:"add_step",
        ajax_module:""
      },
      success: function(response){
            //var pipecontainer = '<div class="col-12 col-sm-6 col-md-4 col-lg-3 col-xlg-2p my-1 pipeline_field"><div class="card mx-auto px-3 h-100" style="width: 16rem;"><div class="card-body ajax-step-"><h5 class="card-title ajax-step-num my-0">Step '+response.step_count+'</div><div class="ajax-form-div ajax-form-step-'+response.step_count+'">'+response.form+'</div></div></div>';
            var pipecontainer = response.form;
            $(pipecontainer).insertAfter("div.col-12:last");
          }
    });
  });

  $(document).on('click',".submit_ajax_steps",function(){
    var descriptions = $('.ajax-description').map(function(){
             return $.trim($(this).val());
          }).get();
    var using_modules = $('.ajax-using_modules').map(function(){
             return $.trim($(this).val());
          }).get();
    var using_functions = $('.ajax-using_functions').map(function(){
             return $.trim($(this).val());
          }).get();
    var outputs = $('.ajax-output').map(function(){
             return $.trim($(this).val());
          }).get();
    var step_nums = $('.step').map(function(){
             return $.trim($(this).attr("id"));
          }).get();
      $.ajax({
        url: '',
        type: 'post',
        data:{
          ajax_type:"post_pipe",
          ajax_description:$('.pipeline-description').val(),
          ajax_title:$('.pipeline-title').val(),
          'descriptions[]':descriptions,
          'using_modules[]':using_modules,
          'using_functions[]':using_functions,
          'outputs[]':outputs,
          'step_nums[]':step_nums
        },
        success: function(response){
          console.log(response)
          if(response.status!="success"){
            $('.pipeline-form-container').html(response.pipe_form);
            var i;
            for (i = 0; i < response.step_nums.length; i++) {
                $('.ajax-form-step-'+response.step_nums[i]).html(response.forms[i]);
            }
            alert(response.status)
          }
          else{window.location.href=response.redirect}
            }
      });
    });
$(document).on('change',".ajax-using_modules",function(){
        console.log($(this).parents(".card").find('.card-title').html())
        $.ajax({
          url: '',
          type: 'post',
          data:{
            ajax_type:"select_modules",
            ajax_step:$(this).parents(".step").attr("id"),
            ajax_module:$(this).val(),
          //ajax_description:$(this).parent().siblings().children(".ajax-description").val(),
            //ajax_output:$(this).parent().siblings().children(".ajax-output").val(),
          },
          success: function(response){
            //console.log($('.ajax-form-step-'+response.step_num).find('.ajax-using_functions'));
              $('.ajax-form-step-'+response.step_num).find('.ajax-using_functions').html(response.options)
              }
        });
      });

      $(document).on('click',".get_stored_param",function(){
              console.log("")

            });
});
