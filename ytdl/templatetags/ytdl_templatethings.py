import colorsys
from django import template


def randomish_colour(inp):
    hues = [x/99.0 for x in range(100)]

    colours = ["rgb(%d, %d, %d)" % colorsys.hsv_to_rgb(h*255, 128, 128) for h in hues]

    return colours[(24 + hash(inp)) % len(colours)]


register = template.Library()
register.filter("randomish", randomish_colour)
