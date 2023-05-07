#Importowanie pakietów
import cv2
import svgwrite
import numpy as np
import svg_to_gcode

##TWORZENIE PLIKU SVG

# Pobieranie zdjęcia do analizy
img = cv2.imread("img/fot4.jpg")
# Skalowanie zdjęcia do 70%
width = int(img.shape[1] * 70 / 100)
height = int(img.shape[0] * 70 / 100)
new_size = (width, height)  
img = cv2.resize(img, new_size)
#wyświetlenie zdjęcia
cv2.imshow('Obraz', img)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Zmiana kolorów obrazu na odcienie szarości
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#zastosowanie fitlra w celu lepszego progowania obrazu
gray = cv2.medianBlur(gray, 5)

# Progowanie obrazu
thresh = cv2.adaptiveThreshold(gray, 200, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
thresh = cv2.bilateralFilter(thresh, 9, 60, 60)

# Szukanie konturów
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)


# Sortowanie konturów wg długości (malejąco)
contours = sorted(contours, key=cv2.contourArea, reverse=True)
# Wybieranie x najdłuższych konturów
x = 1
contours = contours[:x]
# Rysowanie konturów
cv2.drawContours(img, contours, -1, (0, 255, 0), 2)
cv2.imshow('Contours', img)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Wybieramy najdłuższy kontur
contour = max(contours, key=cv2.contourArea)

# Konwersja konturu do postaci złożonej z punktów
curve = np.squeeze(contour)

# Utworzenie pliku SVG i dodanie krzywej do niego
dwg = svgwrite.Drawing('podpis.svg')
path = svgwrite.path.Path(d='M' + str(curve[0][0]) + ',' + str(curve[0][1]))
for point in curve[1:]:
    path.push('L', str(point[0]), ',', str(point[1]))
dwg.add(path)

# Zapisanie pliku SVG
dwg.save()

##KONWERTOWANIE SVG DO GCODE



from svg_to_gcode.svg_parser import parse_file
from svg_to_gcode.compiler import Compiler, interfaces
from svg_to_gcode.formulas import linear_map

# Instantiate a compiler, specifying the custom interface and the speed at which the tool should move.
gcode_compiler = Compiler(interfaces.Gcode, movement_speed=1000, cutting_speed=300, pass_depth=5)

curves = parse_file("podpis.svg") # Parse an svg file into geometric curves

gcode_compiler.append_curves(curves) 
gcode_compiler.compile_to_file("podpis1.gcode")