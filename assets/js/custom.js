
// mobile menu toggle
$(".menu-bar").on('click', function() {
  $(this).addClass('active');
  $('.main_menu').addClass('opened');
});
$(".close_menu").on('click', function() {
  $('.menu-bar').removeClass('active');
  $('.main_menu').removeClass('opened');
});







