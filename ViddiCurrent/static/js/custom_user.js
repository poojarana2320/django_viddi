$(document).ready(function(){
	$('.introContinueBtn').click(function() {
		$('.qnIntroOverlay').css("display","none");
		$('.qnMainContainer').show();
	});


	var prCount = $('.count').html();
	$('#sideQnBtns_'+prCount).addClass('activeQn');
});