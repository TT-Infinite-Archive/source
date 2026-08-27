print('Converts 0-255 RGB to 0-1 RGB')
while True:
	r = float(input('R: '))
	g = float(input('G: '))
	b = float(input('B: '))
	result = (round(r/255.0, 2), round(g/255.0, 2), round(b/255.0, 2), 1.0)
	print(('Vec4%s' % str(result)))
