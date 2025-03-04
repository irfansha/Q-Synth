class Logger:
    def __init__(self, log_level: int) -> None:
        self.log_level = log_level

    def log(self, level: int, message: str, **kwargs) -> None:
        """Log a message if the level is greater than or equal to the logger's log level."""
        if level <= self.log_level:
            print(message, **kwargs)
