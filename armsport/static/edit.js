/**
 * Created by Dexp on 12.04.2017.
 */
function create_form_del(button,first_name,middle_name,last_name,weight) {
    var container = button.parent();
    container.append('<div class="row"><form id="form_edit" method="post"></form></div>');
    var form = button.siblings().children('form');
    form.append(
        '<input name="old_fn"/>' +
        '<input name="old_mn"/>' +
        '<input name="old_ln"/>' +
        '<input name="old_weight"/>' +
        '<button type="submit" name="del" style="display: none"></button>'
    );
    form.children("[name='old_fn']").val(first_name).css('display','none');
    form.children("[name='old_mn']").val(middle_name).css('display','none');
    form.children("[name='old_ln']").val(last_name).css('display','none');
    form.children("[name='old_weight']").val(weight).css('display','none');
}

function create_form_edit(button,first_name,middle_name,last_name,age,weight,team){
    var date = age.split('.')[2] + '-' + age.split('.')[1] + '-' + age.split('.')[0];
    var container = button.parent();
    container.append('<div class="row"><form id="form_edit" method="post"></form></div>');
    var form = button.siblings().children('form');
    form.append('<input name="old_fn"/><input name="old_mn"/><input name="old_ln"/><input name="old_age"/><input name="old_weight"/><input name="old_team"/>' +
        '<div class="col m6 l6 s6"><label for="mn">Фамилия</label><input class="valid" id="mn" name="mn"/></div>' +
        '<div class="col m6 l6 s6"><label for="fn">Имя</label><input class="valid" id="fn" name="fn"/></div>' +
        '<div class="col m6 l6 s6"><label for="ln">Отчество</label><input class="valid" name="ln"/></div>' +
        '<div class="col m6 l6 s6"><label for="age_edit">Дата рождения</label><input type="date" id="age_edit" name="age_edit"/></div>' +
        '<div class="col m6 l6 s6"><label for="weight_edit">Вес</label><input class="valid" id="weight_edit" name="weight_edit"/></div>' +
        '<div class="col m6 l6 s6"><label for="team_edit">Команда</label><input id="team_edit" class="valid" name="team_edit"/></div>' +
        '<div class="col offset-l4 l4 offset-m4 m4 offset-s4 s4">' +
        '<button type="submit" name="edit" class="sub waves-effect waves-light">Готово</button>' +
        '</div>');
    form.children().children("[name='fn']").val(first_name);
    form.children().children("[name='mn']").val(middle_name);
    form.children().children("[name='ln']").val(last_name);
    form.children().children("[name='age_edit']").val(date);
    form.children().children("[name='weight_edit']").val(weight);
    form.children().children("[name='team_edit']").val(team);
    form.children("[name='old_fn']").val(first_name).css('display','none');
    form.children("[name='old_mn']").val(middle_name).css('display','none');
    form.children("[name='old_ln']").val(last_name).css('display','none');
    form.children("[name='old_age']").val(age).css('display','none');
    form.children("[name='old_weight']").val(weight).css('display','none');
    form.children("[name='old_team']").val(team).css('display','none');


};

$('.del').click(function () {
    $('.tooltipped').tooltip('remove');
    var list = $(this).siblings();
    console.log(list);
    var first_name = list[1].innerHTML.split(' ')[1];
    var middle_name = list[1].innerHTML.split(' ')[0];
    var last_name = list[1].innerHTML.split(' ')[2];
    var weight = list[3].innerHTML.split(' ')[1].split('к')[0];
    list.each(function () {
        $(this).remove();
    });
    create_form_del($(this),first_name,middle_name,last_name,weight);
    $('[name="del"]').click();
});

$('.edit').click(function () {
    $('.tooltipped').tooltip('remove');
    var list = $(this).siblings();
    console.log(list);
    var first_name = list[1].innerHTML.split(' ')[1];
    var middle_name = list[1].innerHTML.split(' ')[0];
    var last_name = list[1].innerHTML.split(' ')[2];
    var age = list[2].innerHTML.split(' ')[2];
    var weight = list[3].innerHTML.split(' ')[1].split('к')[0];
    var team = list[4].innerHTML.split(' ')[1];
    list.each(function () {
        $(this).remove();
    });
    console.log(first_name,middle_name,last_name,age,weight,team);
    create_form_edit($(this),first_name,middle_name,last_name,age,weight,team);
    $(this).remove();

    $('[name="fn"],[name="mn"],[name="ln"],[name="team_edit"]').change(function () {
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

    $("#weight_edit").change(function () {
        $(this).removeClass('valid');
        $(this).removeClass('invalid');
        var temp = /^\d{1,3}([\.,]\d{1,3})?$/g;
        var weight_current = $.trim($(this).parent().parent().parent().parent().parent().parent().siblings('.collapsible-header').text()).split(' ')[2].split('к')[0];

        if (weight_current[weight_current.length-1]=="+"){
            if(+$(this).val() > +weight_current && temp.test($(this).val())){
                $(this).addClass('valid');
            }
            else{
                $(this).addClass('invalid');
            }
        }
        else {
            var weight_prev = $(this).parent().parent().parent().parent().parent().parent().parent().prev().children('div').text().split(' ')[2];

            if (weight_prev) {
                weight_prev = weight_prev.split('к')[0];
                if (+$(this).val() > +weight_prev && +$(this).val() <= +weight_current && temp.test($(this).val())) {
                    $(this).addClass('valid');
                }
                else {
                    $(this).addClass('invalid');
                }
            }
            else {
                console.log();
                if (+$(this).val() <= +weight_current && temp.test($(this).val())) {
                    $(this).addClass('valid');
                }
                else {
                    $(this).addClass('invalid');
                }
            }
        }
    });

    $("#form_edit").submit(function () {
        var len = $(this).find('.invalid').length;
        if( len > 0) {
            $('.invalid').animate({opacity: 0}, 1000 );
            $('.invalid').animate({opacity: 1}, 500 );
            return false;
        }
        else return true;
    });
});


$('.settings').click(function () {
    $('.c').css('display','none');
    $('.set').css('display','block');
});

