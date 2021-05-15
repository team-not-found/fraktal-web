from flask import Flask, redirect, url_for, render_template, request, Markup, jsonify
import io, base64
import fraktal_py as fp
from matplotlib.figure import Figure
import numpy as np

def generateEncodedFractalImage(fractal):
	# Preprocessing (?)
	mat = np.log(np.asarray(fractal.density_map) + 1.0)
	# Plotting
	fig = Figure(tight_layout=True)
	ax = fig.subplots()
	ax.matshow(mat)
	ax.axis("off")

	# Encoding
	buf = io.BytesIO()
	fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0, dpi = 600)
	buf.seek(0)
	plot_url = base64.b64encode(buf.getbuffer()).decode("ascii")
	return plot_url

# generate encoded matplotlib image from fractal parameters
def generateFern(fractal_stepsize, fractal_resolution):
	fractal = fp.Fern()
	fractal.generateFractal(int(fractal_resolution.split("_")[0]), int(fractal_resolution.split("_")[1]), int(fractal_stepsize))
	return generateEncodedFractalImage(fractal) 

def generateMandelbrot(fractal_stepsize, fractal_resolution, x0, y0, x1, y1):
	fractal = fp.Mandelbrot()
	fractal.generateFractal(int(fractal_resolution.split("_")[0]), int(fractal_resolution.split("_")[1]), x0, y0, x1, y1, fractal_stepsize)
	return generateEncodedFractalImage(fractal) 

app = Flask(__name__)

# Generate encoded fractal data and html image
@app.route("/update_fractal", methods=["POST"])
def updateFractal():
	# The form data was sent by jQuery and can be catched by 'request.form'
	fractal_type = request.form["type"]
	fractal_stepsize = request.form["stepsize"]
	fractal_resolution = request.form["resolution"]

	if (fractal_type == "fern"):
		plot_url = generateFern(fractal_stepsize, fractal_resolution)
	
	if (fractal_type == "mandelbrot"):
		aspect_ratio = int(fractal_resolution.split("_")[0]) / int(fractal_resolution.split("_")[1])
		plot_url = generateMandelbrot(1000, fractal_resolution, -2, -2/aspect_ratio, 2, 2/aspect_ratio)
	
	plot_fractal = Markup('<img src="data:image/png;base64, {}" id="fractal_image" width="1920" height="1080">'.format(plot_url))
	return jsonify("", render_template("image.html", plot_fractal = plot_fractal))

# Handle zooming
@app.route("/zoom", methods=["POST"])
def zoomInFractal():
	x0 = float(request.form["x0"])
	y0 = float(request.form["y0"])
	x1 = float(request.form["x1"])
	y1 = float(request.form["y1"])

	fractal_resolution = "1920_1080"
	aspect_ratio = int(fractal_resolution.split("_")[0]) / int(fractal_resolution.split("_")[1])

	plot_url = generateMandelbrot(1000, fractal_resolution, x0, y0, x1, y1)
	# Setting the image size by providing the width and height, they are measured in px.
	plot_fractal = Markup('<img src="data:image/png;base64, {}" id="fractal_image" width="1920" height="1080">'.format(plot_url))
	return jsonify("", render_template("image.html", plot_fractal = plot_fractal))

# Render home page from external html file.
@app.route("/")
def home():
	return render_template("index.html", plot_fractal = "")

# Run the server.
if __name__ == "__main__":
	# add debug and doesn't need to rerun after every change
    app.run(debug=True)