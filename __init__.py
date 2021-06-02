from flask import Flask, render_template, request, Markup, jsonify
import io, base64
import fraktal_py as fp
from matplotlib.figure import Figure
import numpy as np

# Generates fractal image from density map, makes preprocessing, saves into buffer and returns it encoded
def generateEncodedFractalImage(fractal):
	# Preprocessing of density map
	mat = np.log(np.asarray(fractal.density_map) + 1.0)
	
	# Plotting fractal matrix object
	fig = Figure(tight_layout=True)
	ax = fig.subplots()
	ax.matshow(mat, cmap="inferno")
	ax.axis("off")

	# Saving image into buffer
	buf = io.BytesIO()
	fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0, dpi = 600)
	buf.seek(0)

	# Encoding image from buffer
	plot_url = base64.b64encode(buf.getbuffer()).decode("ascii")
	return plot_url

# Generate encoded matplotlib image from fractal parameters
# fractal_stepsize -> number of iterations
# fractal_resolution -> resolution of fractal (ex. 1024X640)
def generateFern(fractal_stepsize, fractal_resolution):
	# Generate fractal object
	fractal = fp.Fern()
	# The resolution is in 'width_height' format and we need to preprocess it
	fractal.generateFractal(int(fractal_resolution.split("_")[0]), int(fractal_resolution.split("_")[1]), int(fractal_stepsize))
	# Make encoding
	return generateEncodedFractalImage(fractal) 

# Generate encoded matplotlib image from fractal parameters
# fractal_stepsize -> number of iterations
# fractal_resolution -> resolution of fractal (ex. 1024X640)
# x0 -> lower left corner x
# y0 -> lower left corner y
# x1 -> upper right corner x
# y1 -> upper right corner y
def generateMandelbrot(fractal_stepsize, fractal_resolution, x0, y0, x1, y1):
	# Generate fractal object
	fractal = fp.Mandelbrot()
	# The resolution is in 'width_height' format and we need to preprocess it
	fractal.generateFractal(int(fractal_resolution.split("_")[0]), int(fractal_resolution.split("_")[1]), x0, y0, x1, y1, fractal_stepsize)
	# Make encoding
	return generateEncodedFractalImage(fractal) 

# Initialize flask web server
app = Flask(__name__)

# When the "Generate!" button is pressed this function will be evaluated
# Generates fractal acording to the parameters sent by POST request
# Makes embedding into html file and returns data in encoded json format
@app.route("/update_fractal", methods=["POST"])
def updateFractal():
	# The form data was sent by jQuery and can be catched by 'request.form' as key-value pairs
	# Type of the fractal (fern of mandelbrot)
	fractal_type = request.form["type"]
	# Resolution of the requested output image
	fractal_resolution = request.form["resolution"]

	if (fractal_type == "fern"):
		# For simplicity the number of iterations (40000000) is hard coded
		plot_url = generateFern(40000000, fractal_resolution)
	
	if (fractal_type == "mandelbrot"):
		# Aspect ratio is used to resize pixels conveniently
		# The resolution is in 'width_height' format and we need to preprocess it
		aspect_ratio = int(fractal_resolution.split("_")[0]) / int(fractal_resolution.split("_")[1])
		# For simplicity the number of iterations (1000) is hard coded
		plot_url = generateMandelbrot(1000, fractal_resolution, -2, -2/aspect_ratio, 2, 2/aspect_ratio)
	
	# We convert the encoded 'plot_url' image into an htm 'img' tag with the appropriate parametheers
	plot_fractal = Markup('<img src="data:image/png;base64, {}" id="fractal_image" width="{}" height="{}">'.format(plot_url,
                                                                                                                   fractal_resolution.split("_")[0],
                                                                                                                   fractal_resolution.split("_")[1]))
	# Result is returned as a json object
	return jsonify("", render_template("image.html", plot_fractal = plot_fractal))

# When we click on mandelbrot this function is evaluated
# Generates fractal acording to the parameters sent by POST request
# Makes embedding into html file and returns data in encoded json format
@app.route("/zoom", methods=["POST"])
def zoomInFractal():
	# The zooming coordinates are extracted from the POST request
	x0 = float(request.form["x0"])
	y0 = float(request.form["y0"])
	x1 = float(request.form["x1"])
	y1 = float(request.form["y1"])

	# Aspect ratio is used to resize pixels conveniently
	# The resolution is in 'width_height' format and we need to preprocess it
	fractal_resolution = request.form["fractal_resolution"]
	aspect_ratio = int(fractal_resolution.split("_")[0]) / int(fractal_resolution.split("_")[1])

	# For simplicity the number of iterations (1000) is hard coded
	plot_url = generateMandelbrot(1000, fractal_resolution, x0, y0, x1, y1)
	
	# We convert the encoded 'plot_url' image into an htm 'img' tag with the appropriate parametheers
	plot_fractal = Markup('<img src="data:image/png;base64, {}" id="fractal_image" width="{}" height="{}">'.format(plot_url,
                                                                                                                   fractal_resolution.split("_")[0],
                                                                                                                   fractal_resolution.split("_")[1]))
	# Result is returned as a json object
	return jsonify("", render_template("image.html", plot_fractal = plot_fractal))

# Render home page from external html file.
@app.route("/")
def home():
	return render_template("index.html", plot_fractal = "")
	
@app.route("/documentation") 
def documentation(): 
	return render_template("documentation.html")

# Run the server.
if __name__ == "__main__":
	# This way doesn't need to rerun after every change in the code
    app.run(debug=True)
