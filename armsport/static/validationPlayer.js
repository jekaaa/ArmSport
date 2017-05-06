/**
 * Created by Dexp on 13.01.2017.
 */
$(document).ready(function() {
    $('select').material_select();
    $('.modal').modal( {dismissible: false});
    
});

//Проверка на правильность ввода поля имени, фамилии и отчества
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

//Проверка на правильность ввода поля веса
$("#weight").change(function () {
    $(this).removeClass('valid');
    $(this).removeClass('invalid');
    var temp = /^\d{1,3}([\.,]\d{1,3})?$/g;
    if (temp.test($(this).val()) ) {
        $(this).addClass('valid');
    }
    else {
        $(this).addClass('invalid');
    }
});

//Проверка на наличие инвалидных классов
$("#player").submit(function () {
    var len = $(this).find('.invalid').length;
    if( len > 0) {
        $('.invalid').animate({opacity: 0}, 1000 );
	    $('.invalid').animate({opacity: 1}, 500 );
        return false;
    }
    else return true;
    
});

$("[name='weight_tournament']").change(function (event) {
    $(this).parent().siblings("[name='sub']").children().click();
});

//var tempChecked = null;
//var tempRadio = null;
$("[name='first_foul_1']").each(function (index) {
    if($(this).is("[name='first_foul_1']:checked")){
        $(this).siblings("[name='second_foul_1']").addClass("activator");
    }
});
$("[name='first_foul_2']").each(function (index) {
    if($(this).is("[name='first_foul_2']:checked")){
        $(this).siblings("[name='second_foul_2']").addClass("activator");
    }
});


$("[name='gap'],[name='first_foul_1'],[name='second_foul_1'],[name='first_foul_2'],[name='second_foul_2']").change(function (event) {
    var sub = true;
    var pare = $.trim($(this).parent().parent().siblings('[name="names"]').text()).replace(/\s+/g," ");
    $('.modal-content p').text(pare);
    var winner1 = pare.split(' ')[0] + " " + pare.split(' ')[1];
    var winner2 = pare.split(' ')[2] + " " + pare.split(' ')[3];
    console.log(pare);
    var weight = $.trim($(this).parent().siblings(".select-wrapper").children('input').val());

    if($(this).is("[name='second_foul_1']:checked")) {
        if($(this).siblings("[name='first_foul_1']").is(":checked")) {
            sub = false;
            $(this).parent().parent().parent().siblings(".card-reveal").children("form").children("input").val("Победитель: " + winner2);
            //$('.modal-content input').val("Победитель: " + winner2 + " " + weight);
            //$('#modal1').modal('open');
            tempChecked = $(this);
        }
    }
    if($(this).is("[name='second_foul_2']:checked")) {
        if($(this).siblings("[name='first_foul_2']").is(":checked")) {
            sub = false;
            $(this).parent().parent().parent().siblings(".card-reveal").children("form").children("input").val("Победитель: " + winner1);
            //$('.modal-content input').val("Победитель: " + winner1 + " " + weight);
            //$('#modal1').modal('open');
            tempChecked = $(this);
        }
    }

    if(sub) $(this).parent().siblings("[name='fouls']").children().click();
});


$("[name='close']").click(function () {
    var card_content = $(this).parent().parent().parent().parent().siblings('.card-content');
    card_content.children("[name='winner1']").children('input').prop("checked",false);
    card_content.children("[name='winner2']").children('input').prop("checked",false);
    card_content.children("[name='formfouls']").children("[name='fouls1']").children("[name='second_foul_1']").prop("checked",false);
    card_content.children("[name='formfouls']").children("[name='fouls2']").children("[name='second_foul_2']").prop("checked",false);
    //if(tempChecked)tempChecked.prop("checked",false);
    //if(tempRadio)tempRadio.prop("checked",false);
});

$("[name='winner1'] input,[name='winner2'] input").change(function (event) {
    var pare = $.trim($(this).parent().siblings('[name="names"]').text()).replace(/\s+/g," ");
    $('.modal-content p').text(pare);
    var winner1 = pare.split(' ')[0] + " " + pare.split(' ')[1];
    var winner2 = pare.split(' ')[2] + " " + pare.split(' ')[3];
    console.log(pare);
    var weight = $.trim($(this).parent().siblings(".select-wrapper").children('input').val());
    if($(this).is("[name='winner1'] input:checked")){
        $('.modal-content input').val("Победитель: " + winner1 + " " + weight);
        $(this).parent().parent().siblings(".card-reveal").children("form").children("input").val("Победитель: " + winner1);
    }
    if($(this).is("[name='winner2'] input:checked")){
        $('.modal-content input').val("Победитель: " + winner2 + " " + weight);
        $(this).parent().parent().siblings(".card-reveal").children("form").children("input").val("Победитель: " + winner2);
    }
    tempRadio = $(this);
});
