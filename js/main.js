
var page;
var original_entry;
var previewed = false;

function start_edit() {
	$('#edit_button').text('Loading...');
	$('#page_data').val(original_entry);
	$('#edit_form').slideDown();
	$('#edit_button').text('Cancel Edit');
	return;
}

function cancel_edit() {
	$('#update_button').hide();
	previewed = false;
	$('#entry').html(original_entry);
	$('#edit_form').slideUp();
	$('#edit_button').text('Edit');
}

$(document).ready(function() {
	page = $('#page_title').val().toLowerCase();
	original_entry = $('#entry').html();
	$('#edit_button').toggle(start_edit, cancel_edit);
	$('#edit_form').submit(function(event) {
		$('#entry').html($("#page_data").val());
		event.preventDefault();
	});
	$('#preview_button').click(function(event) {
		$('#entry').html($("#page_data").val());
		$('#update_button').show();
		previewed = true;
		event.preventDefault();
	});
	$('#reset_button').click(function(event) {
		$('#page_data').val(original_entry);
		$('#update_button').hide();
		previewed = false;
		event.preventDefault();
	});
	$('#cancel_button').click(function(event) {
		cancel_edit();
		event.preventDefault();
	});
});
