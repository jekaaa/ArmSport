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
    /*var number = this.id.split('.')[0];
    var event = this.id.split('.')[1];
    var card = $(this).parent().parent().parent().parent();

    $(this).parent().parent().parent().remove();
    console.log($(this).val());
    $.ajax({
        url:"/api/v1/tournament/" + event + "?table=" + number + "&weight=" + $(this).val(),
        success:function(data){
            console.log(data);
            var empty = "";
            var players = "";
            var fouls = "";
            var options = data.tournaments;
            var weight = $(this).val();
            console.log(options);
            var options_DOM = "";
            var li_DOM = "";
            for (let option of options){
                var li = "<li>" + option + "</li>";
                var str = "<option>" + option + "</option>";
                options_DOM += str;
                li_DOM += li;
            }
            console.log(options_DOM,li_DOM);
            if (data.pares.length == 0){
                empty = '<h6 class="center " style="padding:10px">Матчей нет</h6>';
            }
            else{
                players = '<div class="col l12 m12 s12">' + '<h6 class="center">' + 'Тур ' + data.pares[0][0] + '</h6>' +
                '</div>' + '<div name="winner1" class="col m4 l4 s4 ">' +
                '<input class="activator" type="radio" id="test1' + number + '" />' +
                '<label for="test1' + number+ '"></label>' +
                '</div>' + '<div class="col s4 l4 m4 center">Победитель</div>' +
                '<div name="winner2" class="col m4 l4 s4">' +
                '<input class="activator" type="radio" id="test2' + number + '" />' +
                '<label class="right" for="test2' + number + '"></label>' +
                '</div>' + '<div name="names" class="col l12 m12 s12">' +
                '<h6 class="center">' + '<span class="left">' + data.pares[0][1].split(' - ')[0] + '</span>' +
                '<span class="right">' + data.pares[0][1].split(' - ')[1] + '</span>' +
                '</h6>' +
                '</div>';
            }
            card.append('<div class="row card-content" style="padding-top: 0;padding-bottom: 0px">' +
                '<span class="card-title center" style="padding-top:10px">СТОЛ ' + number + '</span>' +
                '<div class="select-wrapper">' + '<span class="caret">▼</span>' + 
                '<input type="text" class="select-dropdown" readonly="true" data-activates="select-options-' + number + "." + event +
                '" value="' + weight + '">' + '<ul id="select-options-' + number + "." + event + '" ' + 'class="dropdown-content select-dropdown">'+
                li_DOM + '</ul>' + '<select id="select-options-' + number + "." + event + '" name="weight_tournament">' + options_DOM + '</select>' + '</div>'+
                '<div class="col m12 s12 l12">' +  '<img src="../static/red.png" class="circle" style="height: 40px">' +
                '<img src="../static/blue.png" class="circle right" style="height: 40px">' + empty + 
                '</div>' +
                players +
                '</div>');
        }
    });

    */
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
            $('.c').css('display','block');
            $('.set').css('display','none');
            sub = false;
            $(this).parent().parent().parent().siblings(".card-reveal").children("form").children("input").val("Победитель: " + winner2);
            //$('.modal-content input').val("Победитель: " + winner2 + " " + weight);
            //$('#modal1').modal('open');
            tempChecked = $(this);
        }
    }
    if($(this).is("[name='second_foul_2']:checked")) {
        if($(this).siblings("[name='first_foul_2']").is(":checked")) {
            $('.c').css('display','block');
            $('.set').css('display','none');
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
    var card_content = $(this).parent().parent().parent().siblings('.card-content');
    card_content.children("[name='winner1']").children('input').prop("checked",false);
    card_content.children("[name='winner2']").children('input').prop("checked",false);
    card_content.children("[name='formfouls']").children("[name='fouls1']").children("[name='second_foul_1']").prop("checked",false);
    card_content.children("[name='formfouls']").children("[name='fouls2']").children("[name='second_foul_2']").prop("checked",false);
    //if(tempChecked)tempChecked.prop("checked",false);
    //if(tempRadio)tempRadio.prop("checked",false);
});

$("[name='winner1'] input,[name='winner2'] input").change(function (event) {
    var pare = $.trim($(this).parent().siblings('[name="names"]').text()).replace(/\s+/g," ");
    $('.c').css('display','block');
    $('.modal-content p').text(pare);
    var winner1 = pare.split(' ')[0] + " " + pare.split(' ')[1];
    var winner2 = pare.split(' ')[2] + " " + pare.split(' ')[3];
    console.log(pare);
    var weight = $.trim($(this).parent().siblings(".select-wrapper").children('input').val());
    if($(this).is("[name='winner1'] input:checked")){
        $('.modal-content input').val("Победитель: " + winner1 + " " + weight);
        $(this).parent().parent().siblings(".card-reveal").children(".c").children("input").val("Победитель: " + winner1);
    }
    if($(this).is("[name='winner2'] input:checked")){
        $('.modal-content input').val("Победитель: " + winner2 + " " + weight);
        $(this).parent().parent().siblings(".card-reveal").children(".c").children("input").val("Победитель: " + winner2);
    }
    tempRadio = $(this);
});

$(".tabs").css("overflow","hidden")