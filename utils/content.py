from utils.song import Song


class Collection:
    """A collection (album or playlist) of songs

    Parameters:
    ----------
    title: str
        The title of the collection.

    Attributes:
    ----------
    title: str
        The title of the collection.
    id: str
        The id of the collection.
    type: str [album, playlist]
        The type of the collection.
    songs: list[Song]
        The songs of the collection.
    artist: str
        The artist of the collection.
    year: str [NA] (optional)
        The year of the collection (if it's an album).
    """

    def __init__(
        self, title: str, id: str, type: str, artist: str, year: str = "NA"
    ) -> None:
        self.title = title
        self.id = id
        self.type = type
        self.year = year
        self.artist = artist

    def set_songs(self, songs: list[Song]) -> None:
        """Set the songs of the collection.

        Parameters:
        ----------
        songs: list[Song]
            The songs of the collection.
        """
        self.songs = songs
