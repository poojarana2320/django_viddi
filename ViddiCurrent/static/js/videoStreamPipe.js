$('#mainRightNav').addClass('disabled');
var resultArray = JSON.parse(queryArray);
var arrayLen = resultArray.DATA.length;
var user_id = document.getElementById("capture-button").getAttribute("data-userid");
var attendDate = document.getElementById("capture-button").getAttribute("data-attenddate");
var totalQtn = totalquestion;
var qtnstart = totalquestion - arrayLen;
Qcount = arrayLen;
QarrCount = qtnstart;
arrCount = 0;
var filearray = 0;
var QtnCount = 0;
var idCount = QarrCount+1;
var preId = idCount-1;
var video_name_last = 'Not Found';
var alert_in_progress = 0;


$('.questions').html(resultArray.DATA[0][0]);
$('.timeOut').html(resultArray.DATA[0][1]);
$('.count').html(QarrCount+1);
$('.countdown').html(resultArray.DATA[0][1]);

var doUpdate = function() {
    $('.countdown').each(function() {
      var count = parseInt($(this).html());
      if (count !== 0) {
        $(this).html(count - 1);
      }
    });
};
$('.introContinueBtn').click(function(){
	$('#capture-button').prop('disabled', false);
	$('#sideQnBtns_'+idCount+'').removeClass('disabled');
	$('#sideQnBtns_'+preId+'').addClass('completed');
	$('#sideQnBtns_'+preId+'').addClass('disabled');
	$('#stop').prop('disabled', true);
});

var size = {width:640,height:360};
var flashvars = {qualityurl: "avq/720p.xml",accountHash:"eedbf42f25d5a20164fe8a481515b223", eid:"zFjVP1", showMenu:"false", mrt:600,sis:0,asv:1,mv:0, dpv:0, ao:0, dup:0, recorderId:interviewId, userId:user_id};

(function() {
	var pipe = document.createElement('script');
	pipe.type = 'text/javascript';
	pipe.async = true;
	pipe.src = ('https:' == document.location.protocol ? 'https://' : 'http://') + 'cdn.addpipe.com/1.3/pipe.js';
	var s = document.getElementsByTagName('script')[0];
	console.log(s);
	console.log(pipe);
	s.parentNode.insertBefore(pipe, s);
})();

function userHasCamMic(cam_number,mic_number, recorderId){
	var cam = cam_number;
	var microphone = mic_number;
	var err = '';
	if (!cam){
		err = err+' please connect cam!!';
	}else if(!microphone){
		err = err +'please connect microphone!!';
	}
	if(err.length){
		alert(err);
		location.reload();
		$('#capture-button').prop('disabled', true);
		$('#stop').prop('disabled', true);
		return false;
	}
	else{
		// alert('please click Start interview to start your interview!')
		$('#capture-button').prop('disabled', false);
	}
}

function onRecorderReady(recorderId, recorderType){
    document.getElementById("capture-button").onclick = function (){
      //trigger the recording process
		document.VideoRecorder.record();
	}
	document.getElementById("stop").onclick = function (){
		//stopped the recording
		document.VideoRecorder.stopVideo();
	}
}

function btRecordPressed(recorderId){
	interval = setInterval(doUpdate, 999);
	var clockTime = resultArray.DATA[arrCount][1] * 1000;
	console.log('At start.....'+clockTime);

	console.log("Start rec..."+Qcount);
	$('#capture-button').prop('disabled', true);
	$('#stop').prop('disabled', false);

  	setTimeclear = setTimeout( function(){
 		document.VideoRecorder.stopVideo();
	},clockTime);

}

function btStopRecordingPressed(recorderId){
	clearInterval(interval);
	clearTimeout(setTimeclear);
	$('#sideQnBtns_'+idCount+'').addClass('completed');
	$('#sideQnBtns_'+idCount+'').addClass('disabled');
	$('#stop').prop('disabled', true);
	console.log("Stop rec..."+Qcount);
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});



function onSaveOk(streamName, streamDuration, userId, cameraName, micName, recorderId, audioCodec, videoCodec, fileType, videoId, audioOnly,location){
	var fileName = resultArray.DATA[filearray][2];
	var location = location;
	var video_name = streamName;
	var videoId = videoId;
  if (practice_flag === "False") {
    var custom_url = '/interviewee/interview/'.concat(interviewId,'/');
  }
  else {
    var custom_url = '/interviewee/interview/practice/';
  }
  $.ajax({
      url : custom_url,
      data: {'candidate_ID':user_id, 'interview_ID': interviewId, 'question_ID':fileName, 'location':location, 'video_name':video_name, 'videoId':videoId},
      headers: {'X-CSRFToken':getCookie('csrftoken')
          ,'sessionid':getCookie('sessionid')
          },
      success : function(data){
        console.log(data);
        if(data != 0){
          console.log('success!!!');
          if(Qcount > 1 ){
            Qcount--;
            arrCount++;
            QarrCount++;
            var slNo = QarrCount+1;
            alert('Video answer completed');
            idCount++;
            preId = idCount - 1;
          $('.qnMainContainer').css("display","none");
          $('.qnIntroOverlay').show();
          $('.questions').html(resultArray.DATA[arrCount][0]);
            $('.timeOut').html(resultArray.DATA[arrCount][1]);
            $('.count').html(slNo);
            $('.countdown').html(resultArray.DATA[arrCount][1]);
          }else{

          }

        QtnCount++;
          filearray++;
        console.log(QtnCount);
        if(QtnCount == arrayLen){
          updateInterviewStatus(QtnCount);
        }
      }else{
        alert('Question not uploaded, please try again!!');
        $('.qnMainContainer').css("display","none");
        $('.qnIntroOverlay').show();
        $('.questions').html(resultArray.DATA[arrCount][0]);
          $('.timeOut').html(resultArray.DATA[arrCount][1]);
          $('.count').html(slNo);
          $('.countdown').html(resultArray.DATA[arrCount][1]);
          $('#capture-button').prop('disabled', false);
        $('#stop').prop('disabled', false);
      }
      },
      error:function(data,exception){
        alert('Something Went Wrong, try again!!');
        $('.qnMainContainer').css("display","none");
      $('.qnIntroOverlay').show();
      $('.questions').html(resultArray.DATA[arrCount][0]);
        $('.timeOut').html(resultArray.DATA[arrCount][1]);
        $('.count').html(slNo);
        $('.countdown').html(resultArray.DATA[arrCount][1]);
        $('#capture-button').prop('disabled', false);
      $('#stop').prop('disabled', false);
      }
  });
}

// function onVideoRecorded(filename,filetype, audioOnly){
// 	var args = Array.prototype.slice.call(arguments);
// 	alert("onVideoRecorded("+args.join(', ')+")");
// }
//
// function onClickUpload(){
//   alert_in_progress = 0;
//   var args = Array.prototype.slice.call(arguments);
// 	alert("onClickUpload("+args.join(', ')+")");
// }
//
// function onVideoUploadFailed(error){
// 	var args = Array.prototype.slice.call(arguments);
// 	alert("onVideoUploadFailed("+args.join(', ')+")");
// }

function onVideoUploadSuccess(filename, filetype, videoId, audioOnly, location) {
    var fileName = resultArray.DATA[filearray][2];
    var location = location;
    var video_name = filename;
    var videoId = videoId;
    var n = video_name.localeCompare(video_name_last);
    if (practice_flag === "False") {
      var custom_url = '/interviewee/interview/'.concat(interviewId,'/');
    }
    else {
      var custom_url = '/interviewee/interview/practice/';
    }

    // alert("video name: " + "\n" + video_name + "\n" + video_name_last);
    if (n == 0 || alert_in_progress == 1) {
      // alert("Ignoring this call")
    } else {
        alert_in_progress = 1;
        $.ajax({
            url: custom_url,
            data: {
                'candidate_ID': user_id,
                'interview_ID': interviewId,
                'question_ID': fileName,
                'location': location,
                'video_name': video_name,
                'videoId': videoId
            },
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'sessionid': getCookie('sessionid')
            },
            success: function(data) {
                console.log(data);
                if (data != 0) {
                    console.log('success!!!');
                    if (Qcount > 1) {
                        var slNo = QarrCount
                        $('.qnMainContainer').css("display", "none");
                        $('.qnIntroOverlay').show();
                        $('.questions').html(resultArray.DATA[arrCount][0]);
                        $('.timeOut').html(resultArray.DATA[arrCount][1]);
                        $('.count').html(slNo);
                        $('.countdown').html(resultArray.DATA[arrCount][1]);
                        Qcount--;
                        arrCount++;
                        QarrCount++;
                        var slNo = QarrCount + 1;
                        idCount++;
                        preId = idCount - 1;
                    }
                    video_name_last = video_name;
                    alert('Video answer completed');
                    QtnCount++;
                    filearray++;
                    console.log(QtnCount);
                    if (QtnCount == arrayLen) {
                        updateInterviewStatus(QtnCount);
                    } else {
                      window.location.reload();
                    }
                } else {
                    alert('Question not uploaded, please try again!!');
                    $('.qnMainContainer').css("display", "none");
                    $('.qnIntroOverlay').show();
                    $('.questions').html(resultArray.DATA[arrCount][0]);
                    $('.timeOut').html(resultArray.DATA[arrCount][1]);
                    $('.count').html(slNo);
                    $('.countdown').html(resultArray.DATA[arrCount][1]);
                    $('#capture-button').prop('disabled', false);
                    $('#stop').prop('disabled', false);
                    window.location.reload();
                }

            },
            error: function(data, exception) {
                alert('Something Went Wrong, try again!!');
                $('.qnMainContainer').css("display", "none");
                $('.qnIntroOverlay').show();
                $('.questions').html(resultArray.DATA[arrCount][0]);
                $('.timeOut').html(resultArray.DATA[arrCount][1]);
                $('.count').html(slNo);
                $('.countdown').html(resultArray.DATA[arrCount][1]);
                $('#capture-button').prop('disabled', false);
                $('#stop').prop('disabled', false);
                window.location.reload();
            }
        });
    }

}


function updateInterviewStatus(QtnCount){
  if (practice_flag === "False") {
    var custom_url = '/interviewee/interview/'.concat(interviewId,'/');
  }
  else {
    var custom_url = '/interviewee/interview/practice/';
  }
	$.ajax({
      url : custom_url,
      data: {'user_id':user_id, 'attendDate': attendDate, 'interviewid':interviewId},
      headers: {'X-CSRFToken':getCookie('csrftoken')
          ,'sessionid':getCookie('sessionid')
          },
	    // type: 'POST',
	    // url: '/interviewee/interview/'.concat(interviewId,'/'),
	    // data: {user_id:user_id, attendDate: attendDate, interviewid:interviewId},
	    success : function(data){
        console.log(data);
        console.log('success!!!');
        // var url = "{% url 'interviewee:dashboard' %}";
			  window.location.href = '/';
	    },
	    error:function(data,exception){
	    	alert('Something Went Wrong!!');
	    }
	});
}
