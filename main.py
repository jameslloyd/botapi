# main.py
from fastapi import FastAPI, Query
from functools import lru_cache
from scrabble_layout import create_scrabble_layout
from scrabble_board import generate_scrabble_board_image
from fastapi.responses import FileResponse
from typing import List

import os
import uvicorn

app = FastAPI(
    title="SentimentBot API",
    description="supporting api for sentimentbot",
    version="0.1.0",
)

SCRABBLE_SCORES = {
    "A": 1, "B": 3, "C": 3, "D": 2, "E": 1,
    "F": 4, "G": 2, "H": 4, "I": 1, "J": 8,
    "K": 5, "L": 1, "M": 3, "N": 1, "O": 1,
    "P": 3, "Q": 10, "R": 1, "S": 1, "T": 1,
    "U": 1, "V": 4, "W": 4, "X": 8, "Y": 4,
    "Z": 10
}

@lru_cache(maxsize=1)
def load_sowpods(sowpods_path: str = "sowpods.txt") -> set:
    with open(sowpods_path, "r") as f:
        return set(line.strip().upper() for line in f if line.strip())

def is_word_in_sowpods(word: str, sowpods_path: str = "sowpods.txt") -> bool:
    """
    Efficiently check if a word is present in the sowpods.txt file.
    """
    word = word.strip().upper()
    sowpods_set = load_sowpods(sowpods_path)
    return word in sowpods_set

def score_word(word: str) -> int:
    if is_word_in_sowpods(word):
        return sum(SCRABBLE_SCORES.get(char.upper(), 0) for char in word)
    return 0

@app.get("/")
async def read_root():
    """
    Root endpoint that returns a welcome message.
    """
    return {"message": "Hello World! This is a FastAPI app."}

@app.get("/check_word")
async def check_word(word: str = Query(..., description="Word to check in Scrabble dictionary")):
    """
    Endpoint to check if a word exists in the sowpods.txt file.
    Returns true or false.
    """
    exists = is_word_in_sowpods(word)
    score = score_word(word)
    return {
        "word": word,
        "exists": exists,
        "score": score
    }

@app.get("/scrabble_layout")
async def get_scrabble_layout(words: List[str] = Query([], description="List of words to include in the layout")):
    """
    Endpoint to generate and return a Scrabble board layout.
    Accepts a list of words as a query parameter.
    """
    # Generate the Scrabble layout with the provided words
    scrabble_layout = create_scrabble_layout(words)
    
    # Return the layout as a JSON response
    return {
        "layout": scrabble_layout
    }

@app.get("/scrabble_board_image")
async def get_scrabble_board_image(
    words: List[str] = Query([], description="List of words to include on the board")
):
    """
    Endpoint to generate a Scrabble board image with the given words.
    Returns the image file.
    """
    # Generate the Scrabble layout
    scrabble_layout = create_scrabble_layout(words)
    # Generate the board image file path
    image_path = generate_scrabble_board_image(scrabble_layout)
    # Return the image as a file response
    return FileResponse(image_path, media_type="image/png", filename="scrabble_board.png")

# It's good practice to only run the server when the script is executed directly.
# For Cloud Run, this part is not strictly necessary as Gunicorn (or a similar ASGI server)
# will be specified in the Procfile or as the CMD/ENTRYPOINT in the Dockerfile.
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=os.getenv("PORT", 8080))
