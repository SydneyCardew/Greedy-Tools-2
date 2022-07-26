import Card_Maker
import json
from Image_Classes import TransposedFont
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


def get_json(path):
    """Pulls a dictionary from the json file"""
    with open(path, 'r+', encoding="utf-8") as dictionary_json:
        dictionary = json.load(dictionary_json)
    return dictionary


def align_dict(height, width, border, l_height, cursor, text_width, text_height, x_height):
    """Returns a dict containing off-sets for all alignments"""
    dict = {
        "centre": {'x': (width - text_width) // 2, 'y': cursor},
        "left": {'x': border, 'y': cursor},
        "right": {'x': (width - text_width) - border, 'y': cursor},
        "v centre": {'x': (width - text_width) // 2, 'y': (height - text_height) // 2},
        "bottom centre": {'x': (width - text_width) // 2, 'y': (height - border) - x_height},
        "bottom left": {'x': border, 'y': (height - border) - x_height},
        "bottom right": {'x': (width - text_width) - border, 'y': (height - border) - x_height},
        "top centre": {'x': (width - text_width) // 2, 'y': border},
        "top left": {'x': border, 'y': border},
        "top right": {'x': (width - text_width) - border, 'y': border}
    }
    return dict


def card_printer(verbosity):
    """Main logic loop"""
    deck = Card_Maker.make_deck()
    # json files loaded into dicts
    layouts = get_json("Data/Layouts.json")
    colours = get_json("Data/Colours.json")
    fonts = {
        'small': ImageFont.truetype(font='Fonts/CaslonAntique.ttf', size=36),
        'normal': ImageFont.truetype(font='Fonts/CaslonAntique.ttf', size=40),
        'title': ImageFont.truetype(font='Fonts/CaslonAntique.ttf', size=64)
    }
    if verbosity > 0:
        print("Making cards.")
    for index, card in enumerate(deck):
        #  progress bar to terminal
        if verbosity > 0:
            print(f"\r|{'|' * index}{'-' * ((len(deck) - 1) - index)} {index//((len(deck) - 1)/100)}%", end='')
        layout = layouts[card.layout]
        h = layout['height']
        w = layout['width']
        b = layout['border']
        l = layout['l_height']
        im = Image.new('RGB', (w, h), color=tuple(layout['bg_colour']))
        d = ImageDraw.Draw(im)
        cursor = b
        for line in layout['layout']:
            line_rule = line.split("|")
            if line_rule[0] == 'blank':
                cursor += l
            elif line_rule[0] == 'horizontal rule':
                x = w - (b * 3)
                d.line([(b * 3, cursor + 20), (x, cursor + 20)], fill=tuple(colours[line_rule[1]]), width=2)
                cursor += 40
            else:
                font = fonts[line_rule[1]]
                font = TransposedFont(font=font, orientation=Image.Transpose.ROTATE_180) \
                    if line_rule[3] == 'inverted' else font
                text = card.card_dictionary[line_rule[4]]
                top_left_x, top_left_y, bottom_right_x, bottom_right_y = d.textbbox((0, 0), text, font=font)
                width = bottom_right_x - top_left_x
                full_height = bottom_right_y - top_left_y
                x_height = d.textbbox((0, 0), 'x', font=font)[2]
                align = align_dict(h, w, b, l, cursor, width, full_height, x_height)
                d.text((align[line_rule[0]]['x'], align[line_rule[0]]['y']), text, font=font, align="center",
                       fill=tuple(colours[line_rule[2]]))
                cursor += (full_height + 10)
        im.save(f"Cards/{str(index).zfill(len(str(len(deck))))} - {card.name}.png")
        im.close()


def main():
    card_printer(1)


if __name__ == "__main__":
    main()
