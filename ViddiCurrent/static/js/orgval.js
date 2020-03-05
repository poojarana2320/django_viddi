
function checkEmail(obj){
    var userName = $(obj).val();   
    console.log(userName);     
    var pattern = /^\b[A-Z0-9._%-]+@[A-Z0-9.-]+\.[A-Z]{2,4}\b$/i ;
    if(!pattern.test(userName))
    {
        $('#usernameError').empty();    
        alert("Enter valid Email");
        $(obj).css('border-color', 'red');
        $("#usernameError").css('color', 'red');
        $("#usernameError").css('font-size', '12px');
        $("#usernameError").css('padding', '4px'); 
    }
    else {              
        var request = $.ajax({
            url: "userDetails.cfm",
            type: "GET",
            data: {username : userName, method : 'checkEmailExist'},
            dataType: "json",
            success: function(data) {                                        
                if(data.STAT == 1) {                    
        
                    $('#usernameError').empty();    
                    $("#usernameError").append(data.MESSAGE);
                    // $("#usernameStatus").val(1);                            
                    $(obj).css('border-color', 'red');
                    $("#usernameError").css('color', 'red');
                    $("#usernameError").css('font-size', '12px');
                    $("#usernameError").css('padding', '4px');                        
                }
                else {                      
        
                    $('#usernameError').empty();
                    $(obj).css('cssText', 'border-color: green !important');
                }   
            }
        }).fail(function (jqXHR, textStatus, error) {            
            console.log(jqXHR.responseText);
        });
    }
}
function organizationAddCheck() {
    $("#formAddOrganization").submit(function (e) {
        var AddOrganization = $("#organizationName").val().trim();
        var orgdes = $("#organizationDescription").val().trim();
        var orgaddress = $("#organizationAddress").val().trim();
        var phonenum = $("#phoneNum").val().trim();
        var phone = $.isNumeric(phonenum);
        var phonenumlen =phonenum.length;
        var fax = $("#fax").val().trim();
        var website = $("#website").val().trim();
         
        if(AddOrganization == "") {
            alert("Enter organization name");
            $('#organizationName').css('border-color', 'red');
            e.preventDefault();
            return false;
        }  
         else if(orgdes == "") {
            alert("Enter organization description");
            $('#organizationDescription').css('border-color', 'red');
            e.preventDefault();
            return false;
        }   
        else if(orgaddress == "") {
            alert("Enter organization Address");
            $('#organizationAddress').css('border-color', 'red');
            e.preventDefault();
            return false;
        }
        else if($('#phoneNum').val() == ""){
            alert("Enter phone number");
            $('#phoneNum').css('border-color', 'red');
            e.preventDefault();
            return false;
        }
        else if(!phone){
            alert("Enter valid phone number");
            $('#phoneNum').css('border-color', 'red');
            e.preventDefault();
            return false;
        }
        else if(phonenumlen > 12 ) {
            alert("Enter valid phone number");
            $('#phoneNum').css('border-color', 'red');
            e.preventDefault();
            return false;
        }
        else if(fax == "") {
            alert("Enter fax");
            $('#fax').css('border-color', 'red');
            e.preventDefault();
            return false;
        }
        else if(website == "") {
            alert("Enter website");
            $('#website').css('border-color', 'red');
            e.preventDefault();
            return false;
        }
    });
    $('#organizationName').on("input",function(){
        $('#organizationName').css('border-color', 'green');
    });
    
    $('#organizationDescription').on("input",function(){
        $('#organizationDescription').css('border-color', 'green');
    });
    $('#organizationAddress').on("input",function(){
        $('#organizationAddress').css('border-color', 'green');
    });
    $('#phoneNum').on("input",function(){
        $('#phoneNum').css('border-color', 'green');
    }); 
    $('#fax').on("input",function(){
        $('#fax').css('border-color', 'green');
    }); 
    $('#website').on("input",function(){
        $('#website').css('border-color', 'green');
    });    
}
$(document).ready(function() {
    organizationAddCheck();
   
});

