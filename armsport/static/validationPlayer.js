/**
 * Created by Dexp on 13.01.2017.
 */
$(document).ready(function() {
    $('select').material_select();
    $('.modal').modal();
});

$("#middle_name,#last_name,#first_name").change(function () {
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

$("#weight").change(function () {
    $(this).removeClass('valid');
    $(this).removeClass('invalid');
    var temp = /^\d{1,3}(\.\d{1,3})?$/g;
    if (temp.test($(this).val()) ) {
        $(this).addClass('valid');
    }
    else {
        $(this).addClass('invalid');
    }
});

$("#player").submit(function () {
    var len = $('.invalid').length
    if( len > 0) {
        $('.invalid').animate({opacity: 0}, 1000 );
	    $('.invalid').animate({opacity: 1}, 500 );
        return false;
    }
    else return true;
    
});

$("[name='weight_tournament']").change(function (event) {
    $(this).parent().siblings("[name='sub']").children().click();
    //$(event.target).parent().siblings("[name='sub']").children().click();
});

var tempChecked = null;
var tempRadio = null;

$("[name='gap'],[name='first_foul_1'],[name='second_foul_1'],[name='first_foul_2'],[name='second_foul_2']").change(function (event) {
    var sub = true;
    var pare = $(this).parent().siblings('[name="names"]').text();
    console.log(pare);
    $('.modal-content p').text(pare);
    var winner1 = $.trim(pare.split('-')[0]);
    var winner2 = $.trim(pare.split('-')[1]);
    var weight = $.trim($(this).parent().siblings(".select-wrapper").children('input').val());
    if($(this).is("[name='second_foul_1']:checked")) {
        if($(this).siblings("[name='first_foul_1']").is(":checked")) {
            sub = false;
            $('.modal-content input').val("Победитель: " + winner2 + " " + weight);
            $('.modal').siblings('a').click();
            tempChecked = $(this);
        }
    }
    if($(this).is("[name='second_foul_2']:checked")) {
        if($(this).siblings("[name='first_foul_2']").is(":checked")) {
            sub = false;
            $('.modal-content input').val("Победитель: " + winner1 + " " + weight);
            $('.modal').siblings('a').click();
            tempChecked = $(this);
        }
    }

    if(sub) $(this).parent().siblings("[name='fouls']").children().click();
});

$("[name='close']").click(function () {
    if(tempChecked)tempChecked.prop("checked",false);
    if(tempRadio)tempRadio.prop("checked",false);
});

$("[name='winner1'] input,[name='winner2'] input").change(function (event) {
    var pare = $(this).parent().siblings('[name="names"]').text();
    $('.modal-content p').text(pare);
    var winner1 = $.trim(pare.split('-')[0]);
    var winner2 = $.trim(pare.split('-')[1]);
    var weight = $.trim($(this).parent().siblings(".select-wrapper").children('input').val());
    if($(this).is("[name='winner1'] input:checked")){
        $('.modal-content input').val("Победитель: " + winner1 + " " + weight);
    }
    if($(this).is("[name='winner2'] input:checked")){
        $('.modal-content input').val("Победитель: " + winner2 + " " + weight);
    }
    tempRadio = $(this);
    $('.modal').siblings('a').click();
});
