popover_options = {'trigger': 'hover'};
tooltip_options = {'html': true};
datatable_options = {
    'bJQueryUI': false,
    'bPaginate': true,
    'sPaginationType': 'bootstrap',
    'bAutoWidth': true,
    'bProcessing': true,
    'bSort': true,
    'aaSorting': [],
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
    show_update_container();
    $('#upd_messages').prepend('<li>'+msg+'</li>');
}

function delete_order(oid, article) {
    var dat = {'oid': oid};
    bootbox.confirm('Wollen Sie die Bestellung für Artikel '+article+' wirklich löschen?',
        function(result) {
            if (result == true) {
                $.post('/orders/api/delete_order/', {'_JSON_': JSON.stringify(dat)},
                    function(res) {
                        if (res['ok'] == true) {
                            location.reload();
                        } else {
                            add_update_message(res['msg']);
                        }
                    }
                );
            } else {
                add_update_message('Löschen abgebrochen!');
            }
        }
    );
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

function edit_student(url) {
    $.get(url, function(res) {
        $('body').append(res);
        $('#edit_student').modal({'show': true});
    });
}

function save_student() {
    var form = $('#student_edit_form');
    var pdata = {};
    var form_data = form.serializeArray();
    $.each(form_data, function() {
        pdata[this.name] = this.value;
    });
    $.post('/core/api/student/save/', {'_JSON_': JSON.stringify(pdata)},
        function(res) {
            $('#edit_student').modal('hide').remove();
            location.reload();
        }
    );
    return false;
}

function get_sum() {
    var sum = 0;
    $(".costs").each(function(i) {
        sum = sum + parseInt($(this).val(), 10);
    });
    return sum;
}

function update_sum() {
    var sum = get_sum();
    var color = '';
    $('#sum').text(sum);
    if (sum != 100) {
        color = 'red';
    } else {
        color = 'green';
    }
    $('#sum').css({'color': color});
}

function check_costs() {
    var sum = get_sum();
    if (sum != 100) {
        return false;
    }
    return true;
}

function check_supplier(url) {
    var sid = $('#id_art_supplier_id').val() || '0';
    var valid = false;
    $.ajax({
        'type': 'POST',
        'async': false,
        'url': url,
        'data': {'_JSON_': JSON.stringify({'sid': sid})},
        success: function (ret_data) {
            valid = ret_data['result'];
        }
    });
    return valid;
}

function check_form(sup_url) {
    if (check_costs() == false) {
        alert('Summe der Kostenstellen muss 100 ergeben.');
        return false;
    }
    if (check_supplier(sup_url) == false) {
        alert('Lieferant ungültig. Bitte einen aus der Liste wählen.');
        return false;
    }
    return true;
}
