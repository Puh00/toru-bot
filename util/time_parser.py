import re

class TimeParser:
    """
    A class that provides useful methods used to parse a simple time
    format.

    I wish there was an immutable option in this godforsaken language.

    Attributes
    ----------
    TIME_UNITS : tuple[str,str,str,str]
        a constant tuple containing all the units supported

    time : str
        The time format consists of a series of integer + unit, where
        the units are [d,h,m,s] for day, hour, minute and seconds. The
        order of the units are ignored, if multiples of the same unit
        exists then only the last occurence will be parsed.

        For instance:
            1d2h3s translates to 1 day 2 hours and 3 seconds,
            3s2h1d translates to 1 day 2 hours and 3 seconds,
            1m3m2m translates to 2 minutes

    Methods
    -------
    to_seconds()
        Returns the time given in seconds
        
    to_string()
        Returns the time given in a human-readable way
    
    static parse_time(time)
        Parses the given time string
    """

    # the units supported by this class
    TIME_UNITS = ("days", "hours", "minutes", "seconds")

    def __init__(self, time: str) -> None:
        """
        Parameters
        ----------
        time : str
            The string to be parsed, must be of the format defined in
            this class
        """
        self.time = time
        self.parsed = TimeParser.parse_time(time)

    def __str__(self) -> str:
        """
        Returns
        -------
        str
            A grammatically correct(?) string containing the time
            information
        """
        return self.to_string()

    def __int__(self) -> int:
        """
        Returns
        -------
        int
            The time in seconds
        """
        return self.to_seconds()

    def to_seconds(self) -> int:
        """Returns the time in seconds

        Returns
        -------
        int
            The time in seconds
        """
        return (
            self.parsed["seconds"]
            + self.parsed["minutes"] * 60
            + self.parsed["hours"] * 3600
            + self.parsed["days"] * 86400
        )

    def to_string(self) -> str:
        """Returns a human-readable version of the given time

        Parameters
        ----------
        time : str
            The string to be parsed, must be of the format defined in
            this class

        Returns
        -------
        str
            A grammatically correct(?) string containing the time
            information
        """

        time = self.parsed

        # adjust the time so they are in bounds
        time["minutes"] += int(time["seconds"] / 60)
        time["seconds"] = time["seconds"] % 60

        time["hours"] += int(time["minutes"] / 60)
        time["minutes"] = time["minutes"] % 60

        time["days"] += int(time["hours"] / 24)
        time["hours"] = time["hours"] % 24

        readable_time = ""

        for unit in TimeParser.TIME_UNITS:
            count = time[unit]
            # do nothing if the time is 0
            if count == 1:
                # if singular then remove the 's' at the end
                readable_time += f"{count} {unit[:-1]} "
            elif count > 1:
                readable_time += f"{count} {unit} "

        # if empty string, also when the time is equal to 0 seconds
        if len(readable_time) == 0:
            readable_time += "0 seconds"

        # a simple substitution that inserts an "and" if possible
        return re.sub(
            r"((?:\d)+ (?:[a-z]){4,}) ((?:\d)+ (?:[a-z]){4,})$",
            r"\1 and \2",
            readable_time.strip(),
        )

    def parse_time(time: str) -> dict[str, int]:
        """A static method for parsing a given time string

        Parameters
        ----------
        time : str
            The string to be parsed, must be of the format defined in
            this class

        Returns
        -------
        dict[str, int]
            A dictionary containing the time info, see below

            {
                "seconds": 11,
                "minutes": 0,
                "hours": 0,
                "days": 1
            }

        Raises
        ------
        ValueError
            If the given time is not parsable/invalid
        """

        # make sure that the whole string is matched
        mo = re.fullmatch(
            r"""
            (?:
                (?P<seconds>(?:\d)*)s |
                (?P<minutes>(?:\d)*)m |
                (?P<hours>(?:\d)*)h   |
                (?P<days>(?:\d)*)d
            )+
            """,
            time,
            re.VERBOSE,
        )

        if not mo:
            raise ValueError("The given time is invalid!")
        else:
            # convert all values to ints and set all missing values to 0
            time_dict = {k: int(v) for (k, v) in mo.groupdict(default=0).items()}
            return time_dict
