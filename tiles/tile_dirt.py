from tile import Tile

class Dirt(Tile):

    def __init__(self) -> None:
        super().__init__()
        self.color = (115,118,83)
