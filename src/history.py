"""Things that record the move history of the game for replay"""
from datetime import datetime
import os
import numpy as np
from logic import timer


class History():
    """File handling and writing down the moves and board states. Don't forget to call close() when done."""

    @timer
    def __init__(self, mode, filename=None, dir=None):
        """Create a file with the given filename. If no filename is given, use the current date and time."""
        if mode not in ["r", "w"]:
            raise ValueError("Mode must be 'r' or 'w'")
        self.mode = mode
        if filename is None:
            filename = "history_" + self.date_filename()
        if not filename.endswith(".txt"):
            self.filename = filename + ".txt"
        else:
            self.filename = filename
        if dir is not None:
            self.filename = dir + "\\" + self.filename
        self.filename = os.path.join(os.getcwd(), self.filename)
        
        # Reading
        if mode == "r":
            self.file = open(self.filename, "r")
            self.moves = list(self.readMoves())
            self.file.seek(0)
            self.n_of_matrices = sum(1 for line in self.file.readlines()) - 1
            self.number_of_moves = len(self.moves)
            return
        # Writing
        if os.path.exists(self.filename):
            print(f"File {self.filename} already exists. Overwriting.")
            # Delete the old file
            os.remove(self.filename)
        self.moves = []
        self.n_of_matrices = 0
        self.number_of_moves = 0
        self.file = open(self.filename, "x")
    
    @timer
    def saveMatrix(self, matrix):
        """Save the matrix to the file"""
        # print(f"SaveMatrix: {str(matrix)}")
        if self.mode == "r":
            raise ValueError("Cannot save matrix in read mode")
        matrix = np.matrix.flatten(matrix)
        str_matrix = str(matrix).replace("[", "").replace("]", "").replace(",", "")
        # print(f"StrMatrix: {str_matrix}")
        self.file.write(str_matrix + "\n")
        self.n_of_matrices += 1

    @timer
    def loadMatrix(self, index):
        """Static. Load the initial matrix from the file."""
        if self.mode == "w":
            raise ValueError("Cannot load matrix in write mode")
        if index >= self.n_of_matrices:
            print(f"Number of matrices out of range: {index} out of {self.n_of_matrices}")
            return None
        self.file.seek(0)
        lines = self.file.readlines()
        # Get the matrix at the given index
        str_matrix = lines[index]
        matrix = [int(num) for num in str_matrix.split()]
        # Convert to a 4x4 matrix
        # print(f"Matrix: {str(matrix)}")
        matrix = np.array(matrix).reshape(4, 4)
        return matrix
    
    @timer
    def saveMove(self, move):
        """Add move to the list of moves. List will be save at the end."""
        if self.mode == "r":
            raise ValueError("Cannot save move in read mode")
        self.moves.append(move)
        self.number_of_moves += 1

    def readMoves(self):
        """Static. Read the moves from the file."""
        if self.mode == "w":
            raise ValueError("Cannot read moves in write mode")
        # Moves are saved in the last line of the file
        self.file.seek(0)
        lines = self.file.readlines()
        assert len(lines) > 0, f"No moves found in the file {self.filename}"
        return lines[-1]
        
    def close(self):
        """Close the file"""
        # Write the moves to the file
        self.file.write("".join(self.moves))
        self.file.close()

    @staticmethod
    def date_filename():
        right_now = datetime.now()
        # Datetime string in format suitable for a filename
        datetime_string = right_now.strftime(format="%Y-%m-%d_%H-%M-%S")
        return datetime_string


if __name__ == "__main__":
    # Testing
    matrix = [[2, 4, 8, 16], [32, 64, 128, 256], [512, 1024, 2048, 2], [4, 8, 16, 32]]
    history = History("w", dir="history", filename="test")
    history.saveMatrix(matrix)
    history.saveMove("U")
    matrix = [[2, 2, 2, 2], [32, 64, 128, 256], [512, 1024, 2048, 2], [4, 8, 16, 32]]
    history.saveMatrix(matrix)
    history.saveMove("D")
    matrix = [[2, 2, 2, 2], [32, 64, 128, 256], [512, 1024, 2048, 2], [4, 4, 4, 4]]
    history.saveMatrix(matrix)
    history.saveMove("R")
    name = history.filename
    print("Before closing:\n")
    print(f"Filename: {name}")
    print(f"Number of matrices: {history.n_of_matrices}")
    print(f"Number of moves: {history.number_of_moves}")
    history.close()

    history = History("r", filename=name)
    print("After opening:\n")
    print(f"Filename: {history.filename}")
    print(f"Number of matrices: {history.n_of_matrices}")
    print(f"Number of moves: {history.number_of_moves}")
    n = history.n_of_matrices
    print(f"\nNumber of matrices: {n}")
    for i in range(n):
        print(str(history.loadMatrix(i)))