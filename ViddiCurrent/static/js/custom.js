function setPost(obj) {
    var post = $(obj).val();
    $('#post_id').val(post);
}

function checkPost() {
    var postValue = $("#post").val();
    if (postValue == 0) {
        alert("post not selected");
    } else {
        $("#questionsModal").modal("show");
    }
}
//Not using now - To disable organisation selection
function checkOrganisation(e) {
    $('#post').find('option[value!=0]').remove();
    var organisationvalue = $(e).val();
    if (organisationvalue == 0) {
        alert("Select Organisation");
    } else {
        $.ajax({
            type: 'GET',
            url: 'model/cfc/questionMaintenance.cfc?method=getPostByOrganisation',
            data: { organisationId: organisationvalue },
            success: function (data) {
                var postData = JSON.parse(data);
                postData = postData.DATA;
                // console.log(postData);
                $.each(postData, function (index, value) {
                    var optionEle = document.createElement("option");
                    $(optionEle).val(value[0]);
                    $(optionEle).html(value[1]);
                    $('#post').append(optionEle);
                });
            }
        });
        $('#addQuestion').prop("disabled", false);
        $('#post').prop("disabled", false);
        $('#questBank').prop("disabled", false);
        $('#interview_question').prop("disabled", false);
        $('#timeout').prop("disabled", false);
        $("#addBtnSpan").html('');
    }
}
//For latest change - To disable organisation selection
function checkOrganisationEdited() {
    var organisationvalue = 1;
    $.ajax({
        type: 'GET',
        url: 'model/cfc/questionMaintenance.cfc?method=getPostByOrganisation',
        data: { organisationId: organisationvalue },
        success: function (data) {
            var postData = JSON.parse(data);
            postData = postData.DATA;
            // console.log(postData);
            $.each(postData, function (index, value) {
                var optionEle = document.createElement("option");
                $(optionEle).val(value[0]);
                $(optionEle).html(value[1]);
                $('#post').append(optionEle);
            });
        }
    });
    $('#addQuestion').prop("disabled", false);
    $('#post').prop("disabled", false);
    $('#questBank').prop("disabled", false);
    $('#interview_question').prop("disabled", false);
    $('#timeout').prop("disabled", false);
    $("#addBtnSpan").html('');
}


$(document).ready(function () {
    if ($('#addQuestion').prop('disabled')) {
        $("#addBtnSpan").html('Please select the organisation to create an interview');
    }
});


$(document).ready(function () {
    var questionDtl = {};
    $('#createInterview').prop("disabled", true);
    $('#id_end_date').prop("type", "date");
    $('#id_start_date').prop("type", "date");
    $('#organisation').find('option').prop("selected", "selected");
    // $('#organisation').getElementsByTagName('option')[2].prop("selected", "selected");
    $("#btnLogid").click(function () {
        var emailFormat = pattern = /^\b[A-Z0-9._%-]+@[A-Z0-9.-]+\.[A-Z]{2,4}\b$/i;
        var email = $("#id_email").val();
        var password = $("#id_password").val();
        var errorMsg = "";
        $("#errorMsg").html("");
        if ($.trim(email).length == 0) {
            $('#id_email').css('border-color', 'red');
            errorMsg = errorMsg + "Please enter the email!!\n";
        }
        if ($.trim(password).length == 0) {
            $('#id_password').css('border-color', 'red');
            errorMsg = errorMsg + "Please enter the Password!!\n";
        }
        if (emailFormat.test(email)) {
            $('#id_email').css('border-color', 'red');
            errorMsg = errorMsg + "Invalid email format!!\n";
        }
        if ($.trim(password).length < 8) {
            $('#id_password').css('border-color', 'red');
            errorMsg = errorMsg + "Password should contain atleast 8 character!!\n";
        }
        if (errorMsg != "") {
            alert(errorMsg);
            return false;
        }
        e.preventDefault();
        return true;
    });

    $('#addQuestion').click(function () {
        var question = $('#interview_question').val().trim();
        var post = $('#post').val();
        // var timeout = $('#timeout').val().trim(); //For latest change - To set default time limit for question as 30 sec
        var timeout = $('#practiceQnTm').val().trim(); //30; For latest change - To set default time limit for question as 30 sec
        // var organisation = $('#organisation').val(); //For latest change - To disable organisation part
        var organisation = 1;
        $('#post_id').val(post);
        var errorMsg = "";

        if (post == 0) {
            $('#post').css('border-color', 'red');
            setTimeout(function () { $('#post').css('border-color', '#ced4da'); }, 5000);
            errorMsg = errorMsg + "Select the post!!\n";
        }

        if (question.length == 0) {
            $('#interview_question').css('border-color', 'red');
            setTimeout(function () { $('#interview_question').css('border-color', '#ced4da'); }, 5000);
            errorMsg = errorMsg + "Enter the question or select the question!!\n";
        }

        if (timeout.length == 0) {
            $('#timeout').css('border-color', 'red');
            setTimeout(function () { $('#timeout').css('border-color', '#ced4da'); }, 5000);
            errorMsg = errorMsg + "Enter the timeout!!\n";
        } else if (!$.isNumeric(timeout)) {
            $('#timeout').css('border-color', 'red');
            setTimeout(function () { $('#timeout').css('border-color', '#ced4da'); }, 5000);
            errorMsg = errorMsg + "Enter the timeout numeric value!!\n";
            $('#timeout').val('');
        }

        if (errorMsg != "") {
            alert(errorMsg);
            return false;
        } else {
            var addedQnCount = 0;
            $(".qnNo").each(function () {
                addedQnCount++;
            });
            var count = addedQnCount;
            count++;
            $("h5").remove(".noQn");
            //var elemnt = '<div class="eachQuestionContainer" ><div class="row" ><div class="col-md-1 col-sm-1 col-xs-12 text-center" ><span class="qnNo" >'+count+'.</span></div><div class="col-md-8 col-sm-8 col-xs-12 Qn" ><p>'+question+'</p></div><div class="col-3 text-center" ><span class="qnTime" >'+timeout+' Sec</span></div></div><div class="row justify-content-end" ><div class="col-md-3 col-sm-3 col-xs-12 actionContainer text-right" ><span class="text-danger" title="Delete" ><i class="fas fa-trash-alt deleteQnFromList"></i></span></div></div></div>';
            //For latest change - To set default time limit for question as 30 sec

            var elemnt = '<div class="eachQuestionContainer" ><div class="row" ><div class="col-md-1 col-sm-1 col-xs-12 text-center" ><span class="qnNo" >' + count + '.</span></div><div class="col-md-8 col-sm-8 col-xs-12 Qn" ><p>' + question + '<span class="text-danger" title="Delete" ><i class="fas fa-trash-alt deleteQnFromList"></i></span></p></div></div></div>';
            $('#questDiv').append(elemnt);
            $('#interview_question').val('');
            $('#timeout').val('');
            var questionDtl = {};
            var getVal = $('#qbj_question').val();
            if (getVal.length) {
                questionDtl = JSON.parse(getVal);
            }
            questionDtl[count] = { "time": timeout, "question": question };
            $('#qbj_question').val(JSON.stringify(questionDtl));

            // var questionDrop = {};
            // var getVal = $('#qbj_question').val();
            // if (getVal.length) {
            //     questionDrop = JSON.parse(getVal);
            // }
            // questionDrop[count] = { "time": timeout, "question": question };
            // $('#qbj_question').val(JSON.stringify(questionDrop));
        }
        var checkVal = $('#qbj_question').val();
        if (checkVal.length) {
            $('#createInterview').prop("disabled", false);
        }
    });
    checkOrganisationEdited();
});
function attachDragDrop() {
    $("#sortable").sortable({
        connectWith: "#sortable"
    });
    // $("#form-row").droppable({
    //     drop: function (questionDrop) {
    //         alert("Sortable Working")
    //     }
    // });
}
function addInterviewQuestions() {
    var addedQnCount = 0;
    $(".qnNo").each(function () {
        addedQnCount++;
    });
    var count = addedQnCount;
    var questionDtl = {};
    var getVal = $('#qbj_question').val();
    if (getVal.length) {
        questionDtl = JSON.parse(getVal);
    }
    // var questionDrop = {};
    // var getVal = $('#qbj_question').val();
    // if (getVal.length) {
    //     questionDrop = JSON.parse(getVal);
    // }    
    var appendString = ''
    $(".checkQuestion").each(function () {
        if ($(this).prop("checked") == true) {
            count++;
            question = $(this).val();
            //For latest change - To set default time limit for question as 30 sec
            timeout = $(this).attr("data-qnTime");
            // timeout = 30;
            var addedQn = $(".Qn p").text().trim();
            console.log(addedQn);
            // appendString = appendString+'<div class="eachQuestionContainer" ><div class="row" ><div class="col-md-1 col-sm-1 col-xs-12 text-center" ><span class="qnNo" >'+count+'.</span></div><div class="col-md-8 col-sm-8 col-xs-12 Qn" ><p>'+question+'</p></div><div class="col-md-3 col-sm-3 col-xs-12 text-center" ><span class="qnTime" >'+timeout+' Sec</span></div></div><div class="row justify-content-end" ><div class="col-md-3 col-sm-3 col-xs-12 actionContainer text-right" ><span class="text-danger" title="Delete" ><i class="fas fa-trash-alt deleteQnFromList"></i></span></div></div></div>';
            //For latest change - To set default time limit for question as 30 sec
            appendString = appendString + '<div class="eachQuestionContainer" ><div class="row" ><div class="col-md-1 col-sm-1 col-xs-12 text-center" ><span class="qnNo">' + count + '.</span></div><div class="col-md-8 col-sm-8 col-xs-12 Qn" ><p>' + question + ' (' + timeout + ' seconds)' + '<span class="text-danger" title="Delete" ><i class="fas fa-trash-alt deleteQnFromList"></i></span></p></div></div></div>';
            questionDtl[count] = { "time": timeout, "question": question };
        }
    });

    $('#sortable').append(appendString);
    attachDragDrop();
    // $('#questDiv').append(appendString);
    $('#qbj_question').val(JSON.stringify(questionDtl));
    var checkVal = $('#qbj_question').val();
    if (checkVal.length) {
        $('.noQn').hide();
        $('#createInterview').prop("disabled", false);
    }
    $('.checkQuestion').prop('checked', false);
    $('#questionsModal').modal("hide");
}

$(document).ready(function () {
    $(".checkQuestion").change(function () {
        var self = this;
        if (this.checked) {
            var checkedQn = $(this).val().trim();
            $(".Qn p").each(function () {
                var questionInList = $(this).text().trim();
                if (questionInList == checkedQn) {
                    alert("Question already exist in list");
                    $(self).prop('checked', false);
                }
            });
        }

    });
    $(document).on("click", ".deleteQnFromList", function () {
        if (confirm("Are you sure?")) {
            $(this).parent().parent().parent().parent().remove();
        }
        if ($('.eachQuestionContainer').length == 0) {
            $('#createInterview').prop("disabled", true);
            $('.noQn').show();
        }
        var count = 1;
        $(".qnNo").each(function () {
            $(this).text(count);
            count++;
        });
    });
});

var opt = $('[data-fil]');
$('#searchUser').on('keyup', function () {
    var val = $.trim(this.value).toUpperCase();
    opt.hide();
    opt.filter(function () {
        return $(this).attr("data-fil").search(val) >= 0
    }).show();
});

var divs = $('div[data-filter]');
$('#searchQn').on('keyup', function () {
    var val = $.trim(this.value).toLowerCase();
    divs.hide();
    divs.filter(function () {
        return $(this).attr("data-filter").search(val) >= 0
    }).show();
});

$(document).ready(function () {
    $("#interview_question").change(function () {
        var addInterviewQn = $("#interview_question").val().trim();
        $(".Qn p").each(function () {
            var questionInList = $(this).text().trim();
            if (questionInList == addInterviewQn) {
                alert("Question already exist in list");
                $('#interview_question').val('');
            }
        });
    });
});

function addQuestion() {
    var practiceQue = $("#practiceQn").val().trim();
    var practiceTime = $("#practiceQnTm").val().trim();
    var timeCheck = $.isNumeric(practiceTime);
    if (practiceQue.length == 0) {
        $('#practiceQue').css('border-color', 'red');
        alert("Enter the question");
        return false;
    } else if (practiceTime.length == 0) {
        $('#practiceTime').css('border-color', 'red');
        alert("Enter the time");
        return false;
    } else if (!timeCheck) {
        $('#practiceTime').css('border-color', 'red');
        alert("Enter the valid time");
        return false;
    }
}

$(document).ready(function () {

    $(".toggle_bar").click(function () {
        $(".menu").toggleClass("active");
        $("section.content").toggleClass("menu-open");
    });

});


$(window).on('load', function () {
    setTimeout(function () { $(".fade").fadeOut(3000); }, 3000);
});


$(document).ready(function () {

    if (Cookies.get('sidebar') == null) {
        Cookies.set('sidebar', '1');
    }

    if (Cookies.get('sidebar') == '0') {
        $("#leftsidebar").toggleClass("active");
        $(".list").toggleClass("menu-open");
        $("section.content").toggleClass("active-c");
        $(".navbar").toggleClass("menu-open");
        $(".O-Click").toggleClass("menu-open");
        $(".Second_Image_O").toggleClass("menu-open");
        $(".Arrow").toggleClass("A-Open");
    }


    $(".Arrow").click(function () {
        $("#leftsidebar").toggleClass("active");
        $(".list").toggleClass("menu-open");
        $("section.content").toggleClass("active-c");
        $(".navbar").toggleClass("menu-open");
        $(".O-Click").toggleClass("menu-open");
        $(".Second_Image_O").toggleClass("menu-open");
        $(".Arrow").toggleClass("A-Open");

        if (Cookies.get('sidebar') == '0') {
            Cookies.set('sidebar', '1');
        } else {
            Cookies.set('sidebar', '0');
        }
    });

});

$('#datepicker1').datepicker({
    dateFormat: 'dd/mm/yy',
});

$('#datepicker2').datepicker({
    dateFormat: 'dd/mm/yy',
});

$(document).ready(function () {
    var strt_d = new Date($("#datepicker1").val());
    var end_d = new Date($("#datepicker2").val());
    strt_d = new Date(strt_d.getTime() + Math.abs(strt_d.getTimezoneOffset() * 60000));
    end_d = new Date(end_d.getTime() + Math.abs(end_d.getTimezoneOffset() * 60000));
    console.log(strt_d);
    console.log(end_d);
    if (isNaN(strt_d)) {  // d.valueOf() could also work
        strt_d = new Date();
    } else {

    }
    if (isNaN(end_d)) {  // d.valueOf() could also work
        end_d = new Date();
    } else {

    }
    strt_d = getFormattedDate(strt_d);
    $("#datepicker1").val(strt_d);
    end_d = getFormattedDate(end_d);
    $("#datepicker2").val(end_d);


    function getFormattedDate(date) {
        var day = date.getDate();
        var month = date.getMonth() + 1;
        if (day < 10) {
            day = '0' + day;
        }
        if (month < 10) {
            month = '0' + month;
        }
        var year = date.getFullYear();
        return day + '/' + month + '/' + year;
    }
});