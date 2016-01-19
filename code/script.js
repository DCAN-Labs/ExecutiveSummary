$(document).ready(function() {

    var t1_tr = $('#t1_tr');

    if(t1_tr.text() != '2400.0') {
        $('#t1_tr').addClass('out-of-range');
    };
});