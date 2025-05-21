from PIL import Image, ImageDraw
import random

def generate_scrabble_board_image(scrabble_layout, tile_folder = 'scrabble_tiles', output_file="scrabble_board.png", padding=5):
    """
    Generates an image of the Scrabble board from the layout.

    Args:
        scrabble_layout (list[list[str]]): 2D list representing the Scrabble board.
        tile_folder (str): Path to the folder containing tile images (e.g., 'A.png', 'B.png', etc.).
        output_file (str): Path to save the generated board image.
        padding (int): Padding (in pixels) around each tile (top, bottom, left, and right).

    Returns:
        None
    """
    # Load the tile images
    tile_images = {}
    for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        tile_images[char] = Image.open(f"{tile_folder}/{char}.png")
    tile_size = tile_images["A"].size  # Assuming all tiles are the same size
    tile_width, tile_height = tile_size

    # Calculate the size of the board with padding
    padded_tile_width = tile_width + 2 * padding
    padded_tile_height = tile_height + 2 * padding
    board_width = len(scrabble_layout[0]) * padded_tile_width
    board_height = len(scrabble_layout) * padded_tile_height

    # Create a blank transparent image for the board
    board_image = Image.new("RGBA", (board_width, board_height), (255, 255, 255, 0))

    # Paste the tiles onto the board with random rotation
    for row_idx, row in enumerate(scrabble_layout):
        for col_idx, char in enumerate(row):
            if char != ".":  # Skip empty tiles (leave them transparent)
                tile = tile_images.get(char.upper(), None)
                if tile:
                    # Apply random rotation
                    rotation_angle = random.uniform(-2, 2)
                    rotated_tile = tile.rotate(rotation_angle, resample=Image.BICUBIC, expand=True)

                    # Calculate position with padding
                    x = col_idx * padded_tile_width + padding
                    y = row_idx * padded_tile_height + padding

                    # Paste the rotated tile onto the board
                    tile_x = x + (tile_width - rotated_tile.size[0]) // 2
                    tile_y = y + (tile_height - rotated_tile.size[1]) // 2
                    board_image.paste(rotated_tile, (tile_x, tile_y), mask=rotated_tile)

    # Save the final board image
    board_image.save(output_file)
    return output_file