import torudb as db


class ToruRpg:
    """
    A server class that represents a simple RPG experience but designed
    directly for Toru-chan.

    This class communicates directly with the backend `torudb` and
    introduces a simplified interface.

    Note that most methods in this class can raise a
    `ServerSelectionTimeoutError` if the server is too busy or simply
    offline

    Attributes
    ----------
    server : int
        the server id

    Methods
    -------
    register(user)
        Registers the given user in the database

    unregister(user)
        Unregisters the given user from the database

    get_detail(user)
        Retrieves the details (such as exp, level) of the given user

    get_exp(user)
        Retrieves the current exp and required exp of the given user
        in a dictionary

    get_level(user)
        Retrieves the level of the given user

    add_exp(user, exp)
        Adds the amount of exp to the user and levels the user up
        accordingly

    calc_exp(level):
        Calculates the exp needed for the given level
    """

    def __init__(self, server: int) -> None:
        """
        Parameters
        ----------
        server: int
            the server id
        """
        self.server = server

    def register(self, user: int) -> bool:
        """Registers the given user in the database

        Parameters
        ----------
        user : int
            The unique user id

        Returns
        -------
        bool
            True if registers successfully, False if the user is
            already registered

        Raises
        ------
        ServerSelectionTimeoutError
            If the server is too busy or not up
        """
        return db.register(user, self.server)

    def unregister(self, user: int) -> bool:
        """Unregisters the given user in the database

        Parameters
        ----------
        user : int
            The unique user id

        Returns
        -------
        bool
            True if unregisters successfully, False if the user is
            not registered to begin with

        Raises
        ------
        ServerSelectionTimeoutError
            If the server is too busy or not up
        """
        return db.unregister(user, self.server)

    def get_detail(self, user: int) -> dict[str, int]:
        """Retrieves the details (such as exp, level) of the given user

        Parameters
        ----------
        user : int
            The unique user id

        Returns
        -------
        dict[str, int]
            A dictionary containing details about the user, see below
            for an exmaple:

            {
                "server": server_id1
                "current_exp": 69
                "required_exp": 420
                "level": 2
            }
            
        Raises
        ------
        ServerSelectionTimeoutError
            If the server is too busy or not up
        """

        # registers the user if not already done so
        if not db.user_has_server(user, self.server):
            db.register(user, self.server)

        return db.get_detail(user, self.server)

    def get_exp(self, user: int) -> dict[str, int]:
        """Retrieves the current exp and required exp of the given user
        in a dictionary

        Parameters
        ----------
        user : int
            The unique user id

        Returns
        -------
        dict[str, int]
            A dictionary containing the keys "current_exp" and
            "required_exp"

        Raises
        ------
        ServerSelectionTimeoutError
            If the server is too busy or not up
        """

        detail = self.get_detail(user, self.server)
        keys_to_extract = ["current_exp", "required_exp"]

        return {key: detail[key] for key in keys_to_extract}

    def get_level(self, user: int) -> int:
        """Retrieves the level of the given user

        Parameters
        ----------
        user : int
            The unique user id

        Returns
        -------
        int
            The level of the given user

        Raises
        ------
        ServerSelectionTimeoutError
            If the server is too busy or not up
        """
        return self.get_detail(user, self.server)["level"]

    def add_exp(self, user: int, exp: int) -> bool:
        """Adds the amount of exp to the user and levels the user up
        accordingly

        Parameters
        ----------
        user : int
            The unique user id

        exp: int
            The amount of exp to add

        Returns
        -------
        bool
            True if the exp updated successfully, else False

        Raises
        ------
        ServerSelectionTimeoutError
            If the server is too busy or not up
        """

        detail = self.get_detail(user)

        detail["current_exp"] += exp

        if detail["current_exp"] >= detail["required_exp"]:
            detail["level"] += 1
            detail["current_exp"] = 0
            detail["required_exp"] = self.calc_exp(detail["level"])

        return db.update(user, self.server, detail)

    def calc_exp(self, level: int) -> int:
        """Calculates the exp needed for the given level

        Parameters
        ----------
        level : int
            The level to calculate exp for

        Returns
        -------
        int
            The exp need for the given level, 0 if the given level is
            invalid (if the level is less or equal to 0)
        """

        # let's pretend this is a super fancy algorithm
        if level < 1:
            return 0

        return int((level * 80) ** 1.051)
