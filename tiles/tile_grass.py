from tile import Tile

class Grass(Tile):

    def __init__(self) -> None:
        super().__init__()
        self.color = (47, 137, 57)
