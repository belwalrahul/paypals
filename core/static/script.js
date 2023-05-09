$(document).ready(function() {
  // Get the current URL
  var current_url = window.location.href;

  // Add the active class to the navbar link that matches the current URL
  $('.nav-link').each(function() {
    var link_url = $(this).attr('href');
    if (current_url.indexOf(link_url) !== -1) {
      $(this).addClass('active');
    }
  });
});

$(document).ready(function() {
  $('.users-owed-btn').on('mouseenter', function() {
    var owed = $(this).data('owed');
    $(this).tooltip({
      title: owed,
      placement: 'bottom'
    }).tooltip('show');
  });
});