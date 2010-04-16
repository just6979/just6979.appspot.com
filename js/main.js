
function fetch_edit_form(page) {
	$("#edit_form").text("Loading...");
	$.get('edit/' + page, function(data) {
	  $('#edit_form').text(data);
	});
}

function reset_edit_form() {

}


$(document).ready(function() {
	$("#edit_button").toggle(
		function() {
			
			fetch_edit_form();
			$("#edit_form").slideDown();
			$("#edit_button").text("Cancel Edit");
			event.preventDefault();
		},
		function() {
			//reset_edit_form();
			$("#edit_form").slideUp();
			$("#edit_button").text("Edit");
			event.preventDefault();
		
		}
	);
 });
