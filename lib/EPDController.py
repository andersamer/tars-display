import logging, os
from PIL import Image,ImageDraw,ImageFont
from lib.waveshare_epd import epd2in13_V4

class EPDController:

    def __init__(self, landscape=True):
        self.logger = logging.getLogger(__name__)
        self.epd = epd2in13_V4.EPD()

        if landscape:
            # If we are in a landscape orientation, then the 
            # width and height are swapped
            self.width = self.epd.height
            self.height = self.epd.width
        else:
            self.width = self.epd.width
            self.height = self.epd.height

        self.logger.info(f'Initialized EPDController. Display dimensions: {self.width}x{self.height}')


    def init(self):
        self.logger.info('Initializing display registers.')
        self.epd.init()

    def reset(self):
        self.logger.info('Performing hardware reset.')
        self.epd.reset()

    def sleep(self):
        self.logger.info('Going to sleep...')
        self.epd.sleep()

    def _clear(self, color=0xff):
        self.epd.Clear(color)

    def clear(self, color=0xff):
        self.logger.info('Clearing display.')
        self.init()
        self._clear()

    def get_buffer(self, image):
        image = image.rotate(180) # Comment this line if you want the bottom of the image by the charging port
        return self.epd.getbuffer(image)

    def _display(self, image, display_func):
        buffer = self.get_buffer(image)
        display_func(buffer)

    def display(self, image):
        self._display(image, self.epd.display)

    def display_fast(self, image):
        self._display(image, self.epd.display_fast)

    def display_partial(self, image):
        self._display(image, self.epd.displayPartial)

    def display_part_base_image(self, image):
        self._display(image, self.epd.displayPartBaseImage)
