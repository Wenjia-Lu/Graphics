test: robot.mdl main.py matrix.py mdl.py display.py draw.py gmath.py
	python3 main.py robot.mdl
	animate frame*
	convert frame* -delay 4.1 basename.gif

clean:
	rm *pyc *out parsetab.py frame*

clear: 
	rm *pyc *out parsetab.py *ppm frame*
