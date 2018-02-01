from __future__ import print_function, unicode_literals
from past.builtins import xrange

from collections import namedtuple
from itertools import cycle

import jinja2
from PIL import Image

Point = namedtuple('Point', ['x', 'y'])
Pixel = namedtuple('Pixel', ['r', 'g', 'b'])
RenderItem = namedtuple('RenderItem', ['color', 'char'])
RenderGroup = list
HTMLImage = list

TEMPLATE = '''
<html>
<head>
    <meta charset="utf-8">
    <title>{{ title }}</title>
    <style type="text/css">
         .img{
            margin: 0px; padding:  0px; line-height:100%; letter-spacing:0px; text-align: center;
            font-size: {{size}}px;
            background-color: {{background}};
            font-family: {{font_family}};
        }
        
    </style>
</head>
<body class="img">
<div class="img">
{% for group in html_image %}
    {% for item in group %}<font color="#{{ item.color }}">{{ item.char }}</font>{% endfor %}
{% endfor %}
</div>
<script>function show() {
  var myWidth = 0, myHeight = 0;
  if( typeof( window.innerWidth ) == 'number' ) {
    //Non-IE
    myWidth = window.innerWidth;
    myHeight = window.innerHeight;
  } else if( document.documentElement && ( document.documentElement.clientWidth || document.documentElement.clientHeight ) ) {
    //IE 6+ in 'standards compliant mode'
    myWidth = document.documentElement.clientWidth;
    myHeight = document.documentElement.clientHeight;
  } else if( document.body && ( document.body.clientWidth || document.body.clientHeight ) ) {
    //IE 4 compatible
    myWidth = document.body.clientWidth;
    myHeight = document.body.clientHeight;
  }
  document.getElementsByTagName('body')[0].setAttribute("height",myHeight);
  document.getElementsByTagName('body')[0].setAttribute("width",myWidth);
  document.getElementsByClassName('img')[0].setAttribute("height",myHeight);
  document.getElementsByClassName('img')[0].setAttribute("width",myWidth);
}</script>
<script>show() </script>
</body>
</html>'''


class Img2HTMLConverter(object):
    def __init__(self,
                 font_size=10,
                 char='■',
                 background='black',
                 title='Image in HTML',
                 font_family='monospace'):
        self.font_size = font_size
        self.background = background
        self.title = title
        self.font_family = font_family
        self.char = cycle(char)

    def convert(self, source):
        image = Image.open(source)

        width, height = image.size
        row_blocks = int(round(float(width) / self.font_size))
        col_blocks = int(round(float(height) / self.font_size))

        html_image = HTMLImage()
        progress = 0.0
        step = 1. / (col_blocks * row_blocks)

        for col in range(col_blocks):
            render_group = RenderGroup()
            for row in range(row_blocks):
                pixels = []
                for y in range(self.font_size):
                    for x in range(self.font_size):
                        point = Point(row * self.font_size + x, col * self.font_size + y)
                        if point.x >= width or point.y >= height:
                            continue
                        pixels.append(Pixel(*image.getpixel(point)[:3]))
                average = self.get_average(pixels=pixels)
                color = self.rgb2hex(average)
                render_item = RenderItem(color=color, char=next(self.char))
                render_group.append(render_item)

                progress += step
                print('\rprogress: {:.2f}%'.format(progress * 100), end='')

            html_image.append(render_group)

        return self.render(html_image)

    def render(self, html_image):
        template = jinja2.Template(TEMPLATE)
        return template.render(
            html_image=html_image,
            size=self.font_size,
            background=self.background,
            title=self.title,
            font_family=self.font_family,
            width=self.font_size * len(html_image[0]) * 2
        )

    @staticmethod
    def rgb2hex(pixel):
        return '{:02x}{:02x}{:02x}'.format(*pixel)

    @staticmethod
    def get_average(pixels):
        r, g, b = 0, 0, 0
        for pixel in pixels:
            r += pixel.r
            g += pixel.g
            b += pixel.b
        base = float(len(pixels))
        return Pixel(
            r=int(round(r / base)),
            g=int(round(g / base)),
            b=int(round(b / base)),
        )
