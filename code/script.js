$(document).ready(function() {

    if($('#t1_tr').text() != '2400.0') {
        $('#t1_tr').addClass('out-of-range');
    };

    $('div.params').draggable();

    $('div.grayords').resizable();

    $('div.grayords').draggable();

    $('div.epi').draggable();

});