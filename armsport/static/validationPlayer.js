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

$("[name='fouls1'] input,[name='fouls2'] input").change(function () {
    console.log($("[name='fouls1']").length)
    //$('.modal').siblings('a').click()
    
});

$("[name='weight_tournament']").change(function (event) {
    console.log($(event.target).siblings())
    $(event.target).parent().siblings("[name='sub']").children().click()
});

$("[name='winner1'] input,[name='winner2'] input").change(function (event) {
    var pare = $(this).parent().siblings('[name="names"]').text()
    $('.modal-content p').text(pare);
    var winner1 = $.trim(pare.split('-')[0]);
    var winner2 = $.trim(pare.split('-')[1]);
    if($(event.target).is("[name='winner1'] input:checked")){
        $('.modal-content input').val("Победитель: " + winner1 + " " + $(event.target).parent().siblings(".select-wrapper").children('input').val());
    }
    if($(event.target).is("[name='winner2'] input:checked")){
        $('.modal-content input').val("Победитель: " + winner2 + " " + $(event.target).parent().siblings(".select-wrapper").children('input').val());
    }
    if(winner1 !="" && winner2 !="") {
        $('.modal').siblings('a').click();
    }
});
/*$("#weight_tournament").change(function () {

    //$(name).ajaxSubmit({url: window.location.href, type: 'post'})
    var form = $(this).parent().parent();
    $(form).ajaxSubmit({url: window.location.href, type: 'post'});

});*/