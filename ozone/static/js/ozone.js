popover_options = {'trigger': 'hover'};
tooltip_options = {};
datatable_options = {
    'bJQueryUI': false,
    'bPaginate': true,
    'sPaginationType': 'bootstrap',
    'bAutoWidth': true,
    'bProcessing': true,
    'bSort': true,
    'oLanguage': {
        'sUrl': '/static/i18n/de_DE.txt'
    }
}

$(document).ready(
    function() {
        $('.pop').each(function() {
            var element = $(this);
            element.popover(popover_options);
        });
        $('.tt').each(function() {
            var element = $(this);
            element.tooltip(tooltip_options);
        });
        $('.dataTable').each(function() {
            var t = $(this);
            t.dataTable(datatable_options);
        });
        $('#upd_close').click(function() {
            $('#upd_container').hide();
        });
    }
);

function show_update_container() {
    var e = $('#upd_container');
    if (e.is(':hidden')) {
        e.show();
    }
}

function add_update_message(msg) {
    $('#upd_messages').prepend('<li>'+msg+'</li>');
}

function delete_student(student_id, name) {
    var dat = {'student_id': student_id};
    bootbox.confirm('Wollen Sie wirklich '+name+' mit allen gespeicherten Anwesenheiten löschen?',
        function(result) {
            if (result == true) {
                $.post('/core/api/student/delete/', {'_JSON_': JSON.stringify(dat)},
                    function(res_data) {
                        location.reload();
                    });
            } else {
                show_update_container();
                add_update_message('Löschen abgebrochen!');
            }
        }
    );
}
