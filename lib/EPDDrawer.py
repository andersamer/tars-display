import os, logging, requests
from PIL import Image,ImageDraw,ImageFont
from io import BytesIO

class EPDDrawer:

    def __init__(self, width, height):
        self.logger = logging.getLogger(__name__)
        
        # Define canvas dimensions
        self.width = width
        self.height = height

        # Create a persistant canvas image and draw function
        self.canvas_image, self.canvas_draw = self._create_blank_image()

        # Define our assets directory
        self.assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'assets')

        # Define fonts
        self.font16 = ImageFont.truetype(os.path.join(self.assets_dir, 'Font.ttc'), 16)
        self.font24 = ImageFont.truetype(os.path.join(self.assets_dir, 'Font.ttc'), 24)
        self.font_inter32 = ImageFont.truetype(os.path.join(self.assets_dir, 'inter.ttf'), 32)
        self.font_inter24 = ImageFont.truetype(os.path.join(self.assets_dir, 'inter.ttf'), 24)
        self.font_inter16 = ImageFont.truetype(os.path.join(self.assets_dir, 'inter.ttf'), 16)
        self.font_inter10 = ImageFont.truetype(os.path.join(self.assets_dir, 'inter.ttf'), 10)
        self.font_libre_baskerville24 = ImageFont.truetype(os.path.join(self.assets_dir, 'libre_baskerville_bold.ttf'), 24)
        self.font_libre_baskerville18 = ImageFont.truetype(os.path.join(self.assets_dir, 'libre_baskerville_bold.ttf'), 18)
        self.font_libre_baskerville16 = ImageFont.truetype(os.path.join(self.assets_dir, 'libre_baskerville_bold.ttf'), 16)
        self.default_font = self.font_libre_baskerville16

        # Define line spacing
        self.line_spacing = 0


    def _create_blank_image(self):
        image = Image.new('1', (self.width, self.height), 255) 
        draw = ImageDraw.Draw(image)
        return image, draw


    def clear_canvas(self, color=0xff):
        self.logger.info('Clearing canvas.')
        self.canvas_image, self.canvas_draw = self._create_blank_image()


    def draw_text(self, pos, text, font=None):
        self.logger.info(f'Drawing text "{text}"')
        if font is None:
            font = self.default_font
        self.canvas_draw.text(pos, text, font=font, fill=0)


    def draw_wrapped_text(self, pos, text, font=None, max_width=None, max_height=None):
        self.logger.info(f'Drawing wrapped text "{text}"')

        if font is None:
            font = self.default_font

        if max_width is None:
            max_width = self.width - pos[0]

        if max_height is None:
            max_height = self.height - pos[1]

        words = text.split()
        lines = []
        current_line = ''

        def get_test_bbox(text):
            return self.canvas_draw.textbbox((0, 0), text, font=font)

        def get_test_bbox_width(text):
            """Utility function to get the width of a given text block"""
            test_bbox = get_test_bbox(text)
            return test_bbox[2] - test_bbox[0]

        def get_test_bbox_height(text):
            """Utility function to get the height of a given text block"""
            test_bbox = get_test_bbox(text)
            return test_bbox[3] - test_bbox[1]

        def split_long_word(word, font, max_width):
            """Utility function to wrap a long word"""

            # Measure a long word character by character until we hit
            # our max width. Then store that part of the word and do 
            # the same with the others
            parts = []
            current_part = ''

            for char in word:
                test_part = current_part + char
                test_part_width = get_test_bbox_width(test_part)
                
                if test_part_width <= max_width:
                    current_part = test_part
                else:
                    if current_part:
                        parts.append(current_part)
                    current_part = char
            
            if current_part:
                parts.append(current_part)

            return parts

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            test_line_width = get_test_bbox_width(test_line)

            if test_line_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    # Only append the line if it isn't empty
                    lines.append(current_line)
                
                # If the line is empty, then that means we'll need to 
                # check if the word itself is too long
                word_bbox_width = get_test_bbox_width(word)
                if word_bbox_width <= max_width:
                    current_line = word
                else:
                    # Break the word into pieces that take up the whole width
                    broken_parts = split_long_word(word, font, max_width)
                    for i, part in enumerate(broken_parts):
                        if i == 0:
                            current_line = part
                        else:
                            lines.append(current_line)
                            current_line = part

        # If we have a left over word, then add that to our lines array
        if current_line:
            lines.append(current_line)

        y = pos[1]

        for line in lines:
            # Draw the lines one by one until we run out of space
            # test_line_height = get_test_bbox_height(line)
            test_line_height = font.size

            # Don't include lines that go outside our bounds
            # if y + test_line_height > max_height:
            #     break  # Stop if text exceeds screen

            self.canvas_draw.text((pos[0], y), line, font=font, fill=0)
            y += test_line_height + self.line_spacing

        return y


    def draw_rectangle(self, top_left, bottom_right, fill=1, outline=0, width=1):
        self.logger.info(f'Drawing a rectangle from {repr(top_left)} to {repr(bottom_right)}.')
        self.canvas_draw.rectangle([top_left, bottom_right], fill=fill, width=width, outline=outline)


    def draw_img(self, pos, img_data):
        self.logger.info("Drawing image data.")
        try:
            width, height = img_data.size
            self.logger.debug(f'Image dimensions: {width}x{height}')
            self.canvas_image.paste(img_data, pos)
        except Exception as e:
            self.logger.error(f'Exception occurred while drawing image data: {repr(e)}')


    def draw_bmp(self, pos, filename):
        self.logger.info(f'Drawing bitmap located at {filename}')

        try:
            bmp = Image.open(os.path.join(self.assets_dir, filename)).convert('1')
            # bmp = bmp.rotate(-90, expand=True) # Images are incorrectly oriented at first
            self.draw_img(self, pos, bmp)
        
        except Exception as e:
            self.logger.error(f'Exception occurred while drawing bitmap: {repr(e)}')


    def download_convert_img(self, url):
        self.logger.info(f'Requesting image at "{url}"')
        response = requests.get(url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        img.thumbnail((self.width, self.height), Image.Resampling.BICUBIC) # Resize the image to at least fit to the screen
        img = img.convert('1') 
        return img


    def draw_img_from_url(self, pos, url):
        self.logger.info(f'Drawing image from url "{url}"')
        img_data = self.download_convert_img(url)
        self.draw_img(pos, img_data)