$(document).ready(function() {

    $('img[src*=SBRef]').width(300).height(110);

    $('img').filter('.raw_rest_img').width(280).height(140);

    $('.t1_tr').each(function(index, element) {

         if ( $(element).text() != '2400.0') {
            $(element).addClass('out-of-range');
        }
    });

    $('.t1_te').each(function(index, element) {

         if ( $(element).text() != '4.97') {
            $(element).addClass('out-of-range');
        }
    });

    $('.t1_x').each(function(index, element) {
         if ( $(element).text() != '1.0') {
            $(element).addClass('out-of-range');
        }
    });

    $('.t1_y').each(function(index, element) {
         if ( $(element).text() != '1.0') {
            $(element).addClass('out-of-range');
        }
    });

    $('.t1_z').each(function(index, element) {

         if ( $(element).text() != '1.0') {
            $(element).addClass('out-of-range');
        }
    });

    $('.epi_frames').each(function(index, element) {

        if ( $(element).text() != '120') {
            $(element).addClass('out-of-range');
        }
    });

    $('.epi_x').each(function(index, element) {
        if ( $(element).text() != '3.8') {
            $(element).addClass('out-of-range');
        }
    });
    $('.epi_y').each(function(index, element) {
        if ( $(element).text() != '3.8') {
            $(element).addClass('out-of-range');
        }
    });
    $('.epi_z').each(function(index, element) {
        if ( $(element).text() != '3.8') {
            $(element).addClass('out-of-range');
        }
    });

    $('.epi_tr').each(function(index, element) {
        if ( $(element).text() != '2100.0') {
            $(element).addClass('out-of-range');
        }
    });

    $('.epi_te').each(function(index, element) {
        if( $(element).text() != '5.0') {
            $(element).addClass('out-of-range');
            }
    });

    $('.t2_x').each(function(index, element) {
         if ( $(element).text() != '1.0') {
            $(element).addClass('out-of-range');
        }
    });

    $('.t2_y').each(function(index, element) {
         if ( $(element).text() != '1.0') {
            $(element).addClass('out-of-range');
        }
    });

    $('.t2_z').each(function(index, element) {

         if ( $(element).text() != '1.0') {
            $(element).addClass('out-of-range');
        }
    });

    $('.t2_tr').each(function(index, element) {

         if ( $(element).text() != '3200.0') {
            $(element).addClass('out-of-range');
        }
    });

    $('.t2_te').each(function(index, element) {

         if ( $(element).text() != '4.97') {
            $(element).addClass('out-of-range');
        }
    });

    $('div.params').draggable();

    $('div.grayords').draggable();

    $('div.epi').draggable();

});
