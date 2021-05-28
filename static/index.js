// Class to store the stage of mandelbrot fractal for the zooming functionality
class mandelbrot {
  // Variables of class
  static width =  1920.0;
  static height = 1080.0;
  static aspect_ratio = this.width/this.height;
  static x0 = -2.0;
  static x1 =  2.0;
  static y0 = this.x0/this.aspect_ratio;
  static y1 = this.x1/this.aspect_ratio;
  static zoomFactor = 1.0;

  // Setter of the rezolution
  static setResolution(new_width, new_height) {
    this.width = new_width;
    this.height = new_height;
    this.aspect_ratio = this.width/this.height;
  }

  // Getter of resolution
  static getResolution() {
    return this.width.toString() + "_" + this.height.toString();
  }

  // Zooming method
  // Zooms into coordinate x and y
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

  // Reset object to original state
  static reset() {
    this.width =  1920.0;
    this.height = 1080.0;
    this.aspect_ratio = this.width/this.height;
    this.x0 = -2.0;
    this.x1 =  2.0;
    this.y0 = this.x0/this.aspect_ratio;
    this.y1 = this.x1/this.aspect_ratio;
    this.zoomFactor = 1.0;
  }
}

// Make variables global to use anywhere in jQuery
globalThis.mandelbrot = mandelbrot;
var clickable = false;
globalThis.clickable = clickable;

// do jQuery functions if the page is loaded
$(document).ready(function() {


  // On button click we send the form information and generate the fractal and display it
  $("#generate").click(function(e) {
    // Prevent default functionality of form button (placing # at the end of link)
    e.preventDefault();
    // Send information with ajax
    $.ajax({
      // Send information to 'updateFractal' function
      url: "/update_fractal",
      // Data sent in 'request.form' dict
      data: {"type":$("#type").val(), "resolution":$("#resolution").val(),"stepsize":$("#stepsize").val()},
      // Type of request
      type: "POST",
      // Type of what it waits back
      dataType: "json",
      // Handle received data if everything succeded
      success: function(response) {
        // Reset mandelbrot to original state
        mandelbrot.reset();
        // Get values from dropdown and set
        resolution = $("#resolution").val();
        resolution_width = parseInt(resolution.slice(0,4));
        resolution_height = parseInt(resolution.slice(5));
        mandelbrot.setResolution(resolution_width, resolution_height);
        
        // Replace response in html
        $(fractal_holder).replaceWith(response);

        // If we selected mandelbrot make clickable
        if($("#type").val() == "mandelbrot") {
          clickable = true;
          // Display small rocket as mouse
          $("#fractal_holder").css('cursor',"url('static/rocket.png'),auto");
        }
        if($("#type").val() == "fern") {
          clickable = false;
          $('#fractal_holder').css('cursor','default');
        }
      }
    });
  });

  // Some random colors for the backround 
  const colors = ["#3CC155", "#2AA7FF", "#1B1B1B", "#FCBC0F", "#F85F36"];

  // Number of balls in the background
  const numBalls = 50;
  const balls = [];

  // Make animation in background
  for (let i = 0; i < numBalls; i++) {
    let ball = document.createElement("div");
    ball.classList.add("ball");
    ball.style.background = colors[Math.floor(Math.random() * colors.length)];
    ball.style.left = `${Math.floor(Math.random() * 100)}vw`;
    ball.style.top = `${Math.floor(Math.random() * 100)}vh`;
    ball.style.transform = `scale(${Math.random()})`;
    ball.style.width = `${Math.random()}em`;
    ball.style.height = ball.style.width;
    
    balls.push(ball);
    document.body.append(ball);
  }

  // Keyframes
  balls.forEach((el, i, ra) => {
    let to = {
      x: Math.random() * (i % 2 === 0 ? -11 : 11),
      y: Math.random() * 12
    };

    let anim = el.animate(
      [
        { transform: "translate(0, 0)" },
        { transform: `translate(${to.x}rem, ${to.y}rem)` }
      ],
      {
        duration: (Math.random() + 1) * 2000, // random duration
        direction: "alternate",
        fill: "both",
        iterations: Infinity,
        easing: "ease-in-out"
      }
    );
  });

  // On double-click on the image send coordinates for zooming
  $(document).bind("click", function(){
    $("#fractal_image").bind("click", function(ev){

      // Do this to not fire multiple POST requests
      $(this).off("click");
      
      // Do this if we have mandelbot selected
      if(clickable) {

        // Disable clicking
        $('#fractal_holder').css('cursor','none');
        clickable = false;

        // Get parameters of image
        var offset = $(this).offset();
        var relativeX = (ev.pageX - offset.left);
        var relativeY = (ev.pageY - offset.top);
     
        // zoom into parameters x and y
        mandelbrot.zoom(relativeX, relativeY);

        // Send data and handle response
        $.post({
          // Send to zoomInFractal() function in python
          url: "/zoom",
          // Send the following data in dict format
          data: {"x0":mandelbrot.x0, "y0":mandelbrot.y0, "x1":mandelbrot.x1, "y1":mandelbrot.y1, "fractal_resolution":mandelbrot.getResolution()},
          // Handle received data if everything succeded
          success: function(response){
            // Replace response in html
            $(fractal_holder).replaceWith(response);
            // Set back rocket and make image clickable again
            $("#fractal_holder").css('cursor',"url('static/rocket.png'),auto");
            clickable = true;
          }
        });
    
      }

    });
  });


});