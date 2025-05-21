import collections

class ScrabbleLayouter:
    """
    Lays out a list of words on a Scrabble-like board.
    """
    def __init__(self, board_size=15, empty_char='.'):
        """
        Initialises the layouter.

        Args:
            board_size (int): The width and height of the board.
            empty_char (str): Character to represent an empty square.
        """
        if not isinstance(board_size, int) or board_size <= 0:
            raise ValueError("board_size must be a positive integer.")
        if not isinstance(empty_char, str) or len(empty_char) != 1:
            raise ValueError("empty_char must be a single character string.")

        self.board_size = board_size
        self.empty_char = empty_char
        self.board = [[self.empty_char for _ in range(board_size)] for _ in range(board_size)]
        # Optional: to keep track of words and their positions if needed later
        self.placed_words_info = []

    def _is_within_bounds(self, r, c):
        """Checks if coordinates (r, c) are within the board."""
        return 0 <= r < self.board_size and 0 <= c < self.board_size

    def _can_place_word_at(self, word, r_start, c_start, direction, is_first_word_on_board):
        """
        Checks if a word can be placed at the specified location and direction.

        Args:
            word (str): The word to place.
            r_start (int): The starting row.
            c_start (int): The starting column.
            direction (str): 'H' for horizontal, 'V' for vertical.
            is_first_word_on_board (bool): True if this is the first word being placed
                                           (or the board is effectively empty for this placement).

        Returns:
            tuple: (can_place, makes_connection)
                   can_place (bool): True if the word can be validly placed.
                   makes_connection (bool): True if the word connects with an existing letter.
        """
        if not word:
            return False, False

        # 1. Check overall word bounds
        if direction == 'H':
            if not (self._is_within_bounds(r_start, c_start) and \
                    self._is_within_bounds(r_start, c_start + len(word) - 1)):
                return False, False
        else:  # 'V'
            if not (self._is_within_bounds(r_start, c_start) and \
                    self._is_within_bounds(r_start + len(word) - 1, c_start)):
                return False, False

        made_at_least_one_connection = False
        
        for i, char_w in enumerate(word):
            r_curr, c_curr = (r_start, c_start + i) if direction == 'H' else (r_start + i, c_start)
            
            board_char = self.board[r_curr][c_curr]

            if board_char != self.empty_char:  # Cell is occupied
                if board_char == char_w:
                    made_at_least_one_connection = True
                else:
                    return False, False  # Conflict: trying to place different letter
            else:  # Cell is empty, check adjacency rules for "parallel touching"
                if not is_first_word_on_board: # This rule applies when board is not empty
                    # Check perpendicular neighbors. If they are occupied, it's an invalid placement
                    # as it would mean laying a word side-by-side without intersection at this point.
                    if direction == 'H':
                        # Check above
                        if r_curr > 0 and self.board[r_curr - 1][c_curr] != self.empty_char:
                            return False, False
                        # Check below
                        if r_curr < self.board_size - 1 and self.board[r_curr + 1][c_curr] != self.empty_char:
                            return False, False
                    else:  # 'V'
                        # Check left
                        if c_curr > 0 and self.board[r_curr][c_curr - 1] != self.empty_char:
                            return False, False
                        # Check right
                        if c_curr < self.board_size - 1 and self.board[r_curr][c_curr + 1] != self.empty_char:
                            return False, False
        
        if is_first_word_on_board:
            # For the first word, no connection is needed, and it should be placed entirely on empty cells.
            # The check for `board_char != self.empty_char` above would have failed if it wasn't all empty.
            return True, False # True for valid, False for "made_connection" (not applicable for first)
        else:
            # For subsequent words, a connection must have been made.
            if not made_at_least_one_connection:
                return False, False 
        
        return True, made_at_least_one_connection

    def _place_word_on_board(self, word, r_start, c_start, direction):
        """Places the word on the internal board."""
        for i, char_w in enumerate(word):
            if direction == 'H':
                self.board[r_start][c_start + i] = char_w
            else:  # 'V'
                self.board[r_start + i][c_start] = char_w
        self.placed_words_info.append({
            'word': word, 'row': r_start, 'col': c_start, 'direction': direction
        })

    def layout_words(self, words):
        """
        Attempts to lay out a list of words on the board.

        Args:
            words (list[str]): A list of words to place.

        Returns:
            list[list[str]]: The board with words placed, or the initial empty board if
                             no words could be placed.
        """
        if not words or not all(isinstance(w, str) for w in words):
            print("Warning: Input must be a list of strings.")
            return self.board
        
        current_words = [word.upper() for word in words if word] # Use uppercase, ignore empty strings

        if not current_words:
            return self.board

        # 1. Place the first word
        first_word = current_words[0]
        placed_first_word = False

        # Try placing horizontally in the center
        r_h_center = self.board_size // 2
        c_h_center = (self.board_size - len(first_word)) // 2
        can_place, _ = self._can_place_word_at(first_word, r_h_center, c_h_center, 'H', is_first_word_on_board=True)
        if can_place:
            self._place_word_on_board(first_word, r_h_center, c_h_center, 'H')
            placed_first_word = True

        if not placed_first_word:
            # Try placing vertically in the center
            r_v_center = (self.board_size - len(first_word)) // 2
            c_v_center = self.board_size // 2
            can_place, _ = self._can_place_word_at(first_word, r_v_center, c_v_center, 'V', is_first_word_on_board=True)
            if can_place:
                self._place_word_on_board(first_word, r_v_center, c_v_center, 'V')
                placed_first_word = True
        
        if not placed_first_word: # Fallback: try at (0,0) if centering fails (e.g. word too long)
            can_place_0h, _ = self._can_place_word_at(first_word, 0, 0, 'H', is_first_word_on_board=True)
            if can_place_0h:
                self._place_word_on_board(first_word, 0, 0, 'H')
                placed_first_word = True
            elif not placed_first_word: # Final fallback for first word
                can_place_0v, _ = self._can_place_word_at(first_word, 0, 0, 'V', is_first_word_on_board=True)
                if can_place_0v:
                    self._place_word_on_board(first_word, 0, 0, 'V')
                    placed_first_word = True


        if not placed_first_word:
            print(f"Could not place the first word: '{first_word}'.")
            # If first word fails, try with the rest of the list as a new layout problem
            if len(current_words) > 1:
                # Reset board for a fresh attempt with the next word as the first.
                self.board = [[self.empty_char for _ in range(self.board_size)] for _ in range(self.board_size)]
                self.placed_words_info = []
                return self.layout_words(current_words[1:]) # Recursive call
            return self.board # No words could be placed at all

        # 2. Place subsequent words
        for word_to_place in current_words[1:]:
            if not word_to_place: continue # Skip empty strings that might have crept in
            
            found_placement_for_this_word = False
            # Iterate through each character of the new word (potential 'hook' letter)
            for i_new_char, char_new in enumerate(word_to_place):
                if found_placement_for_this_word: break
                # Iterate through each cell of the board to find a matching 'anchor' letter
                for r_board in range(self.board_size):
                    if found_placement_for_this_word: break
                    for c_board in range(self.board_size):
                        if self.board[r_board][c_board] == char_new:
                            # Potential intersection found:
                            # word_to_place[i_new_char] could align with board[r_board][c_board]

                            # Try placing Horizontally
                            # Word starts at (r_board, c_board - i_new_char)
                            start_r_h, start_c_h = r_board, c_board - i_new_char
                            can_place_h, connected_h = self._can_place_word_at(
                                word_to_place, start_r_h, start_c_h, 'H', is_first_word_on_board=False
                            )
                            if can_place_h and connected_h:
                                self._place_word_on_board(word_to_place, start_r_h, start_c_h, 'H')
                                found_placement_for_this_word = True
                                break
                            
                            # Try placing Vertically
                            # Word starts at (r_board - i_new_char, c_board)
                            start_r_v, start_c_v = r_board - i_new_char, c_board
                            can_place_v, connected_v = self._can_place_word_at(
                                word_to_place, start_r_v, start_c_v, 'V', is_first_word_on_board=False
                            )
                            if can_place_v and connected_v:
                                self._place_word_on_board(word_to_place, start_r_v, start_c_v, 'V')
                                found_placement_for_this_word = True
                                break
            
            if not found_placement_for_this_word:
                print(f"Could not find a valid placement for word: '{word_to_place}'")
        
        return self.board

    def print_board(self):
        """Prints the current state of the board to the console."""
        print("\nBoard Layout:")
        for row in self.board:
            print(" ".join(row))
        print("\n")

def create_scrabble_layout(words, board_size=15, empty_char=' '):
    """
    High-level function to create a Scrabble-like layout for a list of words.

    Args:
        words (list[str]): The list of words to layout.
        board_size (int): The size of the board (e.g., 15 for 15x15).
        empty_char (str): The character to use for empty cells.

    Returns:
        list[list[str]]: A 2D list representing the board with words.
                         Prints warnings if words cannot be placed.
    """
    try:
        layouter = ScrabbleLayouter(board_size=board_size, empty_char=empty_char)
        final_board = layouter.layout_words(words)
        # You can uncomment the next line if you want to print the board directly from here
        # layouter.print_board()
        return final_board
    except ValueError as e:
        print(f"Error initialising layouter: {e}")
        return [[empty_char for _ in range(board_size)] for _ in range(board_size)]


if __name__ == '__main__':
    # Example Usage:
    example_words_1 = ["PYTHON", "JAVA", "SCRIPT", "HTML", "CSS"]
    print(f"Attempting to lay out: {example_words_1}")
    board1 = create_scrabble_layout(example_words_1, board_size=15)
    for row in board1:
        print(" ".join(row))
    print("-" * 30)

    example_words_2 = ["HELLO", "WORLD", "LAYOUT", "BOARD", "GAME"]
    print(f"Attempting to lay out: {example_words_2}")
    board2 = create_scrabble_layout(example_words_2, board_size=20)
    for row in board2:
        print(" ".join(row))
    print("-" * 30)
    
    example_words_3 = ["NOINTERSECTION", "XYZ", "ABC"] # These might not intersect well
    print(f"Attempting to lay out: {example_words_3}")
    board3 = create_scrabble_layout(example_words_3)
    for row in board3:
        print(" ".join(row))
    print("-" * 30)

    example_words_4 = ["SCRABBLE", "LETTER", "TILE", "BOARD", "SCORE", "WORD", "PLAY"]
    print(f"Attempting to lay out: {example_words_4}")
    board4 = create_scrabble_layout(example_words_4, board_size=25)
    for row in board4:
        print(" ".join(row))
    print("-" * 30)

    example_words_5 = ["LONGESTWORDPOSSIBLEFORTHISBOARDSIZE", "SHORT"] # Testing long word
    print(f"Attempting to lay out: {example_words_5}")
    board5 = create_scrabble_layout(example_words_5, board_size=15)
    for row in board5:
        print(" ".join(row))
    print("-" * 30)

    example_words_6 = ["A", "B", "C"] # Very short words, testing connection logic
    print(f"Attempting to lay out: {example_words_6}")
    board6 = create_scrabble_layout(example_words_6, board_size=5)
    for row in board6:
        print(" ".join(row))
    print("-" * 30)