import json
import cv2
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from sys import argv

IMGPATH = "blank_sheet.png"


with open("cells.json") as f:
    cells = json.load(f)


def put_text_in_box(image, text, top_left, bottom_right, font_path, font_size=20, color=(0, 0, 0)):
    """
    Puts text inside a bounding box on the cv2 image with automatic text wrapping, using PIL for text rendering.

    :param image: Source cv2 image (numpy array).
    :param text: Text string to be put.
    :param top_left: Tuple (x, y) defining the top-left corner of the bounding box.
    :param bottom_right: Tuple (x, y) defining the bottom-right corner of the bounding box.
    :param font_path: Path to a .ttf font file.
    :param font_size: Initial font size.
    :param color: Text color in RGB.
    :return: Image with text (numpy array).
    """

    # Convert the cv2 image to a PIL image
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image_pil)
    font = ImageFont.truetype(font_path, font_size)

    # Calculate text size and wrapping
    x1, y1 = top_left
    x2, y2 = bottom_right
    w, h = x2 - x1, y2 - y1
    lines = []
    line = []

    for word in text.split():
        # Check if adding the word to the line would exceed the width
        line_width, _ = draw.textsize(' '.join(line + [word]), font=font)
        if line_width <= w:
            line.append(word)
        else:
            lines.append(' '.join(line))
            line = [word]

    # Add the last line
    lines.append(' '.join(line))

    # Draw text
    y = y1
    for line in lines:
        draw.text((x1, y), line, fill=color, font=font)
        y += font.getsize(line)[1]

    # Convert back to cv2 image format and update the original image
    cv2_image = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    np.copyto(image, cv2_image)


def sample_cells(players: list[str]) -> dict[str, list[str]]:
    assert 0 < len(players) <= 6

    default_space = cells["all"]
    
    if len(players) < 5:
        default_space += cells["randoms"]

    player_cells = {

    }

    for player in players:
        other_players = players.copy()
        other_players.remove(player)
        player_space = default_space + [i for op in other_players for i in cells.get(op, [])]
        other_players.append("du")
        player_space += [s.format(random.choice(other_players)) for s in cells["parameterized"]]

        sampled_cells = np.random.choice(player_space, replace=False, size=25)
        player_cells[player] = list(sampled_cells)

    print(player_cells)
    return player_cells


def generate_sheets(players):
    sample_space = sample_cells(players)
    assert len(sample_space) == len(players)
    image = cv2.imread(IMGPATH)

    player_sheets = {

    }

    for player in players:
        player_sheets[player] = generate_sheet(sample_space[player], image)

    for p, sheet in player_sheets.items():
        cv2.imwrite(p + ".png", sheet)


def generate_sheet(sample_space: list, image: np.ndarray):
    image = image.copy()

    start = 8, 294
    end = 625, 910

    sliced = image[295:910, 10:625]
    patches = []

    for i in range(0, 5):
        for j in range(0, 5):
            print(sample_space)

            width = 123
            put_text_in_box(
                sliced, sample_space.pop(), (i*width+1, j*width+1), ((i+1)*width, (j+1)*width), font_path="/mnt/c/Windows/Fonts/comic.ttf"
            )

    return image


def main():
    if len(argv) < 2:
        raise ValueError("You have to supply players separated by a comma. example: python generate_sheets.py player1,player2,player3")

    players = argv[1]
    players = players.split(",")
    generate_sheets(players)


if __name__ == "__main__":
    main()