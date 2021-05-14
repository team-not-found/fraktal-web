class mandelbrot {
  static width =  1920.0;
  static height = 1080.0;
  static aspect_ratio = this.width/this.height;
  static x0 = -2.0;
  static x1 =  2.0;
  static y0 = this.x0/this.aspect_ratio;
  static y1 = this.x1/this.aspect_ratio;

  static zoomFactor = 1.0;

  static zoom(x, y) {
    this.zoomFactor *= 2;
    var xValue = (this.x1 - this.x0)*x/this.width + this.x0;
    var yValue = -(this.y1 - this.y0)*y/this.height + this.y1;
    var newX0 = xValue - 1.0/this.zoomFactor;
    var newY0 = yValue - 1.0/this.zoomFactor/this.aspect_ratio;
    var newX1 = xValue + 1.0/this.zoomFactor;
    var newY1 = yValue + 1.0/this.zoomFactor/this.aspect_ratio;
    this.x0 = newX0;
    this.y0 = newY0;
    this.x1 = newX1;
    this.y1 = newY1;
  }
}

// make it global to use in jQuery
globalThis.mandelbrot = mandelbrot;

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

      mandelbrot.zoom(relativeX, relativeY);

      // Send data and handle response
      $.post({
        url: "/zoom",
        data: {"x0":mandelbrot.x0, "y0":mandelbrot.y0, "x1":mandelbrot.x1, "y1":mandelbrot.y1},
        success: function(response){
          // Handle response
          $(fractal_holder).replaceWith(response)
        }
      });
    });
  });

});