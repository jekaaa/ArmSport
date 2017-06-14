/**
 * Created by Dexp on 18.10.2016.
 */
$(document).ready(function() {
    $('select').material_select();
    $('.datepicker').pickadate({
        format: 'dd.mm.yyyy',
        selectYears: 20
  });
});

$("#name").change(function () {
    $(this).removeClass('valid');
    $(this).removeClass('invalid');
    var spaces = /\s+/g;
    var name = $(this).val().replace(spaces,' ');
    if (name.length < 2) {
        $(this).addClass('invalid');
    }
    else {
        $(this).addClass('valid');
    }
});

$('#weight_man,#weight_woman').change(function () {
    $(this).removeClass('valid');
    $(this).removeClass('invalid');
    var temp = /^(\d+(\+)?(\,(\s)?)?)+$/g;
    if (temp.test($(this).val()) ) {
        $(this).addClass('valid');
    }
    else {
        $(this).addClass('invalid');
    }
});

$('#number_table').change(function () {
    $(this).removeClass('valid');
    $(this).removeClass('invalid');
    var temp = /^\d+$/g;
    if (temp.test($(this).val())) {
        $(this).addClass('valid');
    }
    else {
        $(this).addClass('invalid');
    }
});

$("[name='type']").change(function () {
    if($("[name='type'] :selected").index() == 0){
        $("#weight_man").parent().css('display','block');
        $("#weight_woman").parent().css('display','none');
    }
    if($("[name='type'] :selected").index() == 1){
        $("#weight_man").parent().css('display','none');
        $("#weight_woman").parent().css('display','block');
    }
    if($("[name='type'] :selected").index() == 2){
        $("#weight_man").parent().css('display','block');
        $("#weight_woman").parent().css('display','block');
    }
});

$("form").submit(function () {
    var len = $('.invalid:visible').length
    if( len > 0) {
        $('.invalid').animate({opacity: 0}, 1000 );
	    $('.invalid').animate({opacity: 1}, 500 );
        return false;
    }
    else{
        var invisible_list = $('form div:hidden');
        for (var i=0;i<invisible_list.length;i++){
            $(invisible_list[i]).remove();
        }
        return true;
    }
});