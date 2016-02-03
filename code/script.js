$(document).ready(function() {

    var t1Dimensions = Array($('.t1_x'), $('.t1_y'), $('.t1_z'));
    console.log(t1Dimensions.length);

    console.log(t1Dimensions[0].childNodes);

    // grab the text of an id
    var $t1_tr = $('#t1_tr').text();

    //convert that text to a number then check against an expected value
    if(Number($t1_tr) < 2400) {
        console.log($t1_tr + ' is less than 2400');  //delete this later...
        $('#t1_tr').addClass('out-of-range');  //make red if not within range
    }

    //TODO: make objects for data params for more efficient param checks?
    var t1_data = {x: $('.t1_x'),
                    y: $('.t1_y'),
                    z: $('.t1_z')
    };

    //TODO: figure out how loop through an object array... or scrap this method

    function checkT1Values() {
        console.log('x: ' + this.x.text());
        console.log('y: ' + this.y);
        console.log('z: ' + this.z);
        // TODO: for loop here through the object

        if(parseFloat(this.x.text()) != 1) {
            console.log(this.x + ' is out of range!');
            this.x.addClass('out-of-range');
        };
    };

    t1_data.logDetails = checkT1Values;

    t1_data.logDetails();

    //TODO: change all this below here to be more loopy and check for values instead of text!

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

    if($('#epi1_x').text() != '3.8') {
        $('#epi1_x').addClass('out-of-range');
    };

    if($('#epi1_y').text() != '3.8') {
        $('#epi1_y').addClass('out-of-range');
    };

    if($('#epi1_z').text() != '3.8') {
        $('#epi1_z').addClass('out-of-range');
    };

    if($('#epi2_x').text() != '3.8') {
        $('#epi2_x').addClass('out-of-range');
    };

    if($('#epi2_y').text() != '3.8') {
        $('#epi2_y').addClass('out-of-range');
    };

    if($('#epi2_z').text() != '3.8') {
        $('#epi2_z').addClass('out-of-range');
    };
        if($('#epi3_x').text() != '3.8') {
        $('#epi3_x').addClass('out-of-range');
    };

    if($('#epi3_y').text() != '3.8') {
        $('#epi3_y').addClass('out-of-range');
    };

    if($('#epi3_z').text() != '3.8') {
        $('#epi3_z').addClass('out-of-range');
    };
        if($('#epi4_x').text() != '3.8') {
        $('#epi4_x').addClass('out-of-range');
    };

    if($('#epi4_y').text() != '3.8') {
        $('#epi4_y').addClass('out-of-range');
    };

    if($('#epi4_z').text() != '3.8') {
        $('#epi4_z').addClass('out-of-range');
    };

    if($('#epi5_x').text() != '3.8') {
        $('#epi5_x').addClass('out-of-range');
    };

    if($('#epi5_y').text() != '3.8') {
        $('#epi5_y').addClass('out-of-range');
    };

    if($('#epi5_z').text() != '3.8') {
        $('#epi5_z').addClass('out-of-range');
    };
    $('div.params').draggable();

    $('div.grayords').resizable();

    $('div.grayords').draggable();

    $('div.epi').draggable();

});
