$(document).ready(function() {

    if($('#t1_tr').text() != '2400.0') {
        $('#t1_tr').addClass('out-of-range');
    };

    if($('.t1_x').text() != '1.0') {
        $('.t1_x').addClass('out-of-range');
    };

    if($('.t1_y').text() != '1.0') {
        $('.t1_y').addClass('out-of-range');
    };

    if($('.t1_z').text() != '1.0') {
        $('.t1_z').addClass('out-of-range');
    };

    if($('.t2_x').text() != '1.0') {
        $('.t2_x').addClass('out-of-range');
    };

    if($('.t2_y').text() != '1.0') {
        $('.t2_y').addClass('out-of-range');
    };

    if($('.t2_z').text() != '1.0') {
        $('.t2_z').addClass('out-of-range');
    };

    if($('#epi1_te').text() != '5.0') {
        $('#epi1_te').addClass('out-of-range');
    };

    if($('#epi2_te').text() != '5.0') {

        $('#epi2_te').addClass('out-of-range');
    };

    if($('#epi3_te').text() != '5.0') {

        $('#epi3_te').addClass('out-of-range');
    };

    if($('#epi4_te').text() != '5.0') {

        $('#epi4_te').addClass('out-of-range');
    };

    if($('#epi5_te').text() != '5.0') {

        $('#epi5_te').addClass('out-of-range');
    };

    if($('#epi1_frames').text() != '120') {

        $('#epi2_frames').addClass('out-of-range');
    };

    if($('#epi2_frames').text() != '120') {

        $('#epi2_frames').addClass('out-of-range');
    };

    if($('#epi3_frames').text() != '120') {

        $('#epi2_frames').addClass('out-of-range');
    };

    if($('#epi4_frames').text() != '120') {

        $('#epi2_frames').addClass('out-of-range');
    };

    if($('#epi5_frames').text() != '120') {

        $('#epi2_frames').addClass('out-of-range');
    };

    $('div.params').draggable();

    $('div.grayords').resizable();

    $('div.grayords').draggable();

    $('div.epi').draggable();

});
