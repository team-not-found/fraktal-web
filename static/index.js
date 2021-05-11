$(document).ready(function() {
  
  // On button click we send the form information and generate the fractal and display it
  $("#generate").click(function(e) {
    e.preventDefault();
    $.ajax({
      // Send information to 'updateFractal' function
      url: "/update_fractal",
      // Data sent in 'request.form' dict
      data: {"type":$("#type").val(), "resolution":$("#resolution").val(),"stepsize":$("#stepsize").val()},
      type: "POST",
      // What it waits back
      dataType: "json",
      // Handle received data
      success: function(response) {
        $(fractal_holder).replaceWith(response);
      }
    });
  });

  // On click on the image send coordinates for zooming
  $(document).bind("click", function(){
    $("#fractal_image").bind("click", function(ev){
      // To not fire multiple POST requests
      $(this).off("click");

      // Get parameters of image
      var offset = $(this).offset();
      var relativeX = (ev.pageX - offset.left);
      var relativeY = (ev.pageY - offset.top);

      // Send data and handle response
      $.post({
        url: "/zoom",
        data: {"img_x":relativeX, "img_y":relativeY},
        success: function(response){
          // Handle response
        alert("word");
        }
      });
    });
  });
});