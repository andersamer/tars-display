#!venv/bin/python

import sys, os, logging, time
from PIL import Image,ImageDraw,ImageFont
from pprint import pprint

from lib.waveshare_epd import epd2in13_V4
from lib.EPDController import EPDController
from lib.EPDDrawer import EPDDrawer
from lib.SpotifyHandler import SpotifyHandler

def init_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    # Suppress noisy logs
    log_sources_to_suppress = [
        # 'urllib3.connectionpool',
        # 'urllib3.util.retry',
        # 'lib.waveshare_epd.epd2in13_V4',
        # 'lib.waveshare_epd.epdconfig'
    ]
    for log_source in log_sources_to_suppress:
        logging.getLogger(log_source).setLevel(logging.WARNING)

    return logging.getLogger(__name__)


def main():

    # Initialize logging
    logger = init_logging()

    logger.info("epd2in13_V4 Demo")

    try:
    
        spotify = SpotifyHandler()

        controller = EPDController()
        drawer = EPDDrawer(controller.width, controller.height)
        controller.init()

        def update_display_info(controller, drawer, song_name, artist_name, album_art_url):
            MARGIN_TOP = 10
            RIGHT_LIMIT = 120
            drawer.clear_canvas()
            song_name_height = drawer.draw_wrapped_text((0, MARGIN_TOP), song_name, font=drawer.font_libre_baskerville24, max_width=RIGHT_LIMIT)
            padding = controller.height - (16 + MARGIN_TOP)
            if song_name_height > padding:
                drawer.clear_canvas()
                song_name_height = drawer.draw_wrapped_text((0, MARGIN_TOP), song_name, font=drawer.font_libre_baskerville18, max_width=RIGHT_LIMIT)
                if song_name_height > padding:
                    drawer.clear_canvas()
                    song_name_height = drawer.draw_wrapped_text((0, MARGIN_TOP), song_name, font=drawer.font_libre_baskerville16, max_width=RIGHT_LIMIT)
            drawer.draw_wrapped_text((0, song_name_height + 10), artist_name, font=drawer.font_inter16, max_width=RIGHT_LIMIT)
            drawer.draw_img_from_url((128, 0), spotify_data['album_art_url'])
            controller.display(drawer.canvas_image)

        last_item_id = None
        WAIT_INTERVAL = 10
        while True:
            spotify_data = spotify.get_currently_playing()

            if spotify_data is None or not spotify_data.get('is_playing'):
                logger.info('Nothing is playing.')
            else:
                current_item_id = spotify_data['item_id']
                if current_item_id != last_item_id:
                    song_name = spotify_data['song_name']
                    artist_name = spotify_data['artist_name']
                    album_art_url = spotify_data['album_art_url']
                    logger.info(f'New track detected: "{song_name}" by "{artist_name}"')
                    update_display_info(controller, drawer, song_name, artist_name, album_art_url)
                    last_item_id = current_item_id
                else:
                    logger.info('Same track is still playing, no update needed.')

            time.sleep(WAIT_INTERVAL)

    except IOError as e:
        logger.error(repr(e))
    except Exception as e:
        logger.error(f'Exception occurred: {repr(e)}')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:    
        # logger.warning('Received interrupt. Quitting...')
        # Make sure you do this at the end so that all threads are closed 
        controller.sleep()
        epd2in13_V4.epdconfig.module_exit(cleanup=True)
        exit()
    