$(document).ready(function() {
  $('#changelist .filters').css('display', 'flex');
  $('.form-inline div select').select2({ dropdownAutoWidth : true });
  initializeAddRow();
  initializeAddSubrow();
});

function selected_option(option) {
  var queryDict = {};
  var current_get_params = extract_url_params(location.search);
  var new_get_params = extract_url_params(option);

  if (new_get_params.length >= current_get_params.length && current_get_params != {} && new_get_params != {}) {
    for(var key in current_get_params){
      queryDict[key] = current_get_params[key];
    }
  }

  for(var key in new_get_params){
    queryDict[key] = new_get_params[key];
  }

  delete queryDict[""];
  var queryString = Object.keys(queryDict).map(key => key + '=' + queryDict[key]).join('&');

  if (queryDict != "") {
    location = window.location.pathname + "?" + queryString;
  }
  else {
    location = window.location.pathname;
  }
}

function extract_url_params(pack) {
  var params = {};
  var pack_split = pack.substr(1).split("&");

  pack_split.forEach(function(item) {
    var key = item.split("=")[0];
    var value = item.split("=")[1]
    params[key] = value;

    if (key.includes('__isnull')) {
      var prefix = item.split('__isnull')[0] + '__';
      if ((pack.split(prefix).length - 1) > 1) {
        delete params[key];
      }
    }
  });

  return params;
}

function dictToURI(dict) {
  var str = [];
  for(var p in dict){
     str.push(encodeURIComponent(p) + "=" + encodeURIComponent(dict[p]));
  }
  return str.join("&");
}

$('.message-close').on('click', function(){
    var message = $(this).parent().parent().parent();
    message.remove();
});

function initializeSelect2(selectElementObj) {
    var existent = selectElementObj.parent().find('span.select2');
    if (existent) {
      existent.remove();
    }
    selectElementObj.select2({ dropdownAutoWidth : true, width: 'auto' });
    initializeAddSubrow();
}

function initializeAddRow(){
    $('.add-row').on('click', function(){
      var total_forms = $(this).parent().find('input[id*="TOTAL_FORMS"]')[0];
      var inline_group = $(this).parent();

      var inline_related_empty_form = inline_group.find('.inline-related.empty-form')[0];
      var element = inline_related_empty_form.id.split('-')[0];
      var regex_empty = new RegExp(element + '-empty', "g");
      var regex_prefix = new RegExp(element + '-__prefix__', "g");

      var inline_related_html = $(inline_related_empty_form.outerHTML.replace(regex_prefix, element + '-' + total_forms.value).replace(/#\d+/, '#' + (parseInt(total_forms.value)+1)).replace(regex_empty, element + '-' + total_forms.value).replace('empty-form', ''));

      total_forms.value = parseInt(total_forms.value)+1;
      inline_related_html.insertBefore(inline_related_empty_form);

      inline_related_html.find("div[id*='datepicker']").datetimepicker({format: 'YYYY-MM-DD'});
      inline_related_html.find("div[id*='datetimepicker']").datetimepicker({});
      initializeSelect2($(".inline-related").not(".empty-form").find("select"));
  });
}

function initializeAddSubrow(){
  $("select.select2-hidden-accessible").each(function(){
    $(this).data('select2').on('opening', function (e) {
      var offset = this.$element.offset().top - 300;
      $('html, body').animate({
          scrollTop: offset
      }, 500);
    });
  });

  $(".add-subrow").unbind('click');
  $('.add-subrow').on('click', function(){
      var total_forms = $(this).parent().parent().parent().parent().parent().find('input[id*="TOTAL_FORMS"]')[0];
      var inline_group = $(this).parent().parent().parent().parent();
      var inline_related_empty_form = inline_group.find('.empty-form')[0];

      var inline_related_html = $(inline_related_empty_form.outerHTML.replace(/__prefix__/g, total_forms.value).replace(/#\d+/, '#' + (parseInt(total_forms.value)+1)).replace(/-empty/g, '-' + total_forms.value).replace(/empty-form/g, ''));
      total_forms.value = parseInt(total_forms.value)+1;
      inline_related_html.insertBefore($(this).parent().parent().parent()[0]);

      inline_related_html.find("div[id*='datepicker']").datetimepicker({format: 'YYYY-MM-DD'});
      inline_related_html.find("div[id*='datetimepicker']").datetimepicker({});
  });
}

$('.selectpicker.ajax').each(function(){
   var this_selectpicker = $(this);
   var data_app_label = $(this).attr('data-app-label');
   var data_ajax__url = $(this).attr('data-ajax--url');
   var data_model = $(this).attr('data-model');
   var data_queryset__lookup = $(this).attr('data-queryset--lookup');

   var _changeInterval = null;
   $(this).on('loaded.bs.select', function (e, clickedIndex, isSelected, previousValue) {
        $(this).parent().find(".bs-searchbox input").on('keyup', function(e) {
            var value = this.value;
            var charTyped = String.fromCharCode(e.which);

            if (/[a-zA-Z0-9\b\0 ]/i.test(charTyped)) {
              var options = this_selectpicker.find('option.generated');
              for(var option of options) {
                  option.remove();
              }
              this_selectpicker.selectpicker('refresh');

                clearInterval(_changeInterval)
                _changeInterval = setInterval(function() {
                    clearInterval(_changeInterval);

                    // Typing finished, now you can Do whatever after 2 sec
                    var jsonObj = {
                        "app_label": data_app_label,
                        "model": data_model,
                        "page_size": 100,
                        "q": value
                    };

                    var filter_list = {};
                    $.ajax({
                        type: 'GET',
                        dataType: "json",
                        data: jsonObj,
                        url: data_ajax__url,
                        async: false,
                        success: function(response) {
                            filter_list = response;
                        }
                    });

                    var params = extract_url_params(location.search);

                    for(var i of filter_list.items) {
                        params[data_queryset__lookup] = i.id

                        this_selectpicker.append($('<option>', {
                            value: "?" + dictToURI(params),
                            text: i.text,
                            class: "generated"
                        }));
                    }

                    this_selectpicker.selectpicker('refresh');
                }, 500);
            }
        });
   });
});
