
$(document).ready(function() {
	$("#edit_button").toggle(
		function() {
			$("#edit_form").slideDown();
			$("#edit_button").text("Cancel Edit");
			event.preventDefault();
		},
		function() {
			$("#edit_form").slideUp();
			$("#edit_button").text("Edit");
			event.preventDefault();
		
		}
	);
 });

