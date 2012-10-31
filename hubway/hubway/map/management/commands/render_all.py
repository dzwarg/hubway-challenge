from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from optparse import make_option

import json
from os import stat, path
from glob import glob
from PythonMagick import Image, DrawableLine, DrawableStrokeColor, DrawableStrokeOpacity, DrawableStrokeWidth

class Command(BaseCommand):
    help = """Render all network trips. Trips must have been routed 
        previously with the "route_all" command."""
    option_list = BaseCommand.option_list + (
        make_option('-n', '--number',
            action='store',
            dest='number',
            default=10,
            type=int,
            help='The number of route batches to combine into a single frame.'),
        make_option('-i', '--input',
            action='store',
            dest='input',
            default='data',
            help='The input folder for the route GeoJSON files.'),
        make_option('-o', '--output',
            action='store',
            dest='output',
            default='data',
            help='The output folder for the composite route image.'),
    )

    bounds = (-71.14645, 42.31182, -71.0357002, 42.38643,)
    scale = 720.0 / (bounds[3] - bounds[1])

    def proj(self, coord):
        return [
            (coord[0] - self.bounds[0]) * self.scale,
            720 - (coord[1] - self.bounds[1]) * self.scale
        ]
    
    def handle(self, *args, **options):
        routes = glob(options['input']+'/routes-*.json')
        routes = sorted(routes, lambda x,y:cmp(stat(path.abspath(x))[8], stat(path.abspath(y))[8]))

        segment = 0
        img = None
        for route in routes:
            self.stdout.write('Opening route "%s"\n' % route)
            rfile = open(route, 'r')
            fc = json.load(rfile)
            rfile.close()

            if segment == 0:
                self.stdout.write('Creating image file.\n')
                img = Image('1280x720', 'white')
                img.draw(DrawableStrokeColor('black'))
                img.draw(DrawableStrokeOpacity(0.01))
                img.draw(DrawableStrokeWidth(1.0))

            for i,feature in enumerate(fc['features']):
                coords = feature['geometry']['coordinates']
                coords = map(lambda x:self.proj(x), coords)
                for start,end in zip(coords[0:-1],coords[1:]):
                    img.draw(DrawableLine(start[0], start[1], end[0], end[1]))

            segment += 1

            if segment == options['number']:
                self.stdout.write('Writing image file "%s.png".\n' % route)
                img.write(route + '.png')
                segment = 0

