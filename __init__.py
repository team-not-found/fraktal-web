from flask import Flask, redirect, url_for, render_template, request, Markup, jsonify
import io, base64
import fraktal_py as fp
from matplotlib.figure import Figure
import numpy as np


class Mandelbrot():
	width = 1920.0
	height = 1080.0
	aspect_ratio = width/height
	x0 = -2.0
	x1 = 2.0
	y0 = x0/aspect_ratio
	y1 = x1/aspect_ratio

	isActive = False
	zoomFactor = 1.0

	def zoom(x, y):
		Mandelbrot.zoomFactor *= 2

		xValue = (Mandelbrot.x1 - Mandelbrot.x0)*x/Mandelbrot.width + Mandelbrot.x0
		yValue = -(Mandelbrot.y1 - Mandelbrot.y0)*y/Mandelbrot.height + Mandelbrot.y1

		newX0 = xValue - 1.0/Mandelbrot.zoomFactor
		newY0 = yValue - 1.0/Mandelbrot.zoomFactor/Mandelbrot.aspect_ratio

		newX1 = xValue + 1.0/Mandelbrot.zoomFactor
		newY1 = yValue + 1.0/Mandelbrot.zoomFactor/Mandelbrot.aspect_ratio

		Mandelbrot.x0 = newX0
		Mandelbrot.x1 = newX1
		Mandelbrot.y0 = newY0
		Mandelbrot.y1 = newY1

	def reset():
		Mandelbrot.width = 1920.0
		Mandelbrot.height = 1080.0
		Mandelbrot.aspect_ratio = Mandelbrot.width/Mandelbrot.height
		Mandelbrot.x0 = -2.0
		Mandelbrot.x1 = 2.0
		Mandelbrot.y0 = Mandelbrot.x0/Mandelbrot.aspect_ratio
		Mandelbrot.y1 = Mandelbrot.x1/Mandelbrot.aspect_ratio

		Mandelbrot.isActive = False
		Mandelbrot.zoomFactor = 1.0




# generate encoded matplotlib image from fractal parameters
def generateEncodedFractalImage(fractal_type, fractal_stepsize, fractal_resolution):
	if fractal_type == "fern":
		Mandelbrot.reset()
		fractal = fp.Fern()
		fractal.generateFractal(int(fractal_resolution.split("_")[0]), int(fractal_resolution.split("_")[1]), int(fractal_stepsize))
		# Preprocessing (?)
		mat = np.log(np.asarray(fractal.density_map) + 1.0)

		# Plotting
		fig = Figure(tight_layout=True)
		ax = fig.subplots()
		ax.matshow(mat)
		ax.axis("off")

		# Encoding
		buf = io.BytesIO()
		fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0)
		buf.seek(0)
		plot_url = base64.b64encode(buf.getbuffer()).decode("ascii")

		return plot_url

	if fractal_type == "mandelbrot":
		fractal = fp.Mandelbrot()

		width = Mandelbrot.width
		height = Mandelbrot.height

		print("Generating mandelbrot ", width, height, Mandelbrot.x0, Mandelbrot.y0, Mandelbrot.x1, Mandelbrot.y1, 1000)

		fractal.generateFractal(int(width), int(height), Mandelbrot.x0, Mandelbrot.y0, Mandelbrot.x1, Mandelbrot.y1, 1000)
		# Preprocessing (?)
		mat = np.log(np.asarray(fractal.density_map))

		# Plotting
		fig = Figure(tight_layout=True)
		ax = fig.subplots()
		ax.matshow(mat)
		ax.axis("off")

		# Encoding
		buf = io.BytesIO()
		fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0, dpi = 300)
		buf.seek(0)
		plot_url = base64.b64encode(buf.getbuffer()).decode("ascii")
		Mandelbrot.isActive = True

		return plot_url

	return ""

app = Flask(__name__)

plot_fractal = ""
img_x = ""
img_y = ""

# Generate encoded fractal data and html image
@app.route("/update_fractal", methods=["POST"])
def updateFractal():
	# The form data was sent by jQuery and can be catched by 'request.form'
	fractal_type = request.form["type"]
	fractal_stepsize = request.form["stepsize"]
	fractal_resolution = request.form["resolution"]
	plot_url = generateEncodedFractalImage(fractal_type, fractal_stepsize, fractal_resolution)
	# Setting the image size by providing the width and height, they are measured in px.
	plot_fractal = Markup('<img src="data:image/png;base64, {}" id="fractal_image" width="1920" height="1080">'.format(plot_url))
	return jsonify("", render_template("image.html", plot_fractal = plot_fractal))

# Handle zooming
@app.route("/zoom", methods=["POST"])
def zoomInFractal():
	img_x = request.form["img_x"]
	img_y = request.form["img_y"]

	if Mandelbrot.isActive: 
		Mandelbrot.zoom(float(img_x), float(img_y))

	plot_url = generateEncodedFractalImage("mandelbrot", 1000, "1920_1080")
	# Setting the image size by providing the width and height, they are measured in px.
	plot_fractal = Markup('<img src="data:image/png;base64, {}" id="fractal_image" width="1920" height="1080">'.format(plot_url))
	return jsonify("", render_template("image.html", plot_fractal = plot_fractal))

# Render home page from external html file.
@app.route("/")
def home():
	return render_template("index.html", plot_fractal = plot_fractal)

# Run the server.
if __name__ == "__main__":
	# add debug and doesn't need to rerun after every change
    app.run(debug=True)