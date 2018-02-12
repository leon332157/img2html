from img2html.converter import Img2HTMLConverter
import os

converter = Img2HTMLConverter(font_size=4, background='black')
html = converter.convert(os.getcwd() + '/gta.jpg')
with open(os.getcwd() + '/a.html', mode='w') as f:
    f.write(str(html))
