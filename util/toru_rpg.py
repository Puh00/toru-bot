import torudb as db


class ToruRpg:
    def __init__(self, server: int) -> None:
        self.server = server

    def register(self, user: int) -> bool:
        return db.register(user, self.server)

    def get_detail(self, user: int) -> dict[str, int]:
        # registers the user if not already done so
        if not db.user_has_server(user, self.server):
            db.register(user, self.server)

        return db.get_detail(user, self.server)

    def get_exp(self, user: int) -> dict[str, int]:
        detail = self.get_detail(user, self.server)
        keys_to_extract = ["current_exp", "required_exp"]

        return {key: detail[key] for key in keys_to_extract}

    def get_level(self, user: int) -> int:
        return self.get_detail(user, self.server)["level"]

    def add_exp(self, user: int, exp: int) -> bool:
        detail = self.get_detail(user)

        detail["current_exp"] += exp

        if detail["current_exp"] >= detail["required_exp"]:
            detail["level"] += 1
            detail["current_exp"] = 0
            detail["required_exp"] = self.calc_exp(detail["level"])

        return db.update(user, self.server, detail)

    def calc_exp(self, level: int) -> int:
        # let's pretend this is a super fancy algorithm
        if level < 1:
            return 0

        return int((level * 80) ** 1.051)
