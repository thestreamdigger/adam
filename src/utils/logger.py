class Logger:
    LEVELS = {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50,
        "WAIT": 21,
        "OK": 22
    }

    def __init__(self, settings=None):
        self.enabled = True
        self.level = "INFO"
        self.format = settings.get('logging', {}).get('format') if settings else "[{level}] {message}"
        
        if settings:
            self.enabled = settings.get('logging', {}).get('enable', True)
            self.level = settings.get('logging', {}).get('level', 'INFO').upper()

    def _log(self, level, message):
        if not self.enabled or self.LEVELS[self.level] > self.LEVELS[level]:
            return
            
        print(self.format.format(
            level=level,
            message=message
        ))

    def debug(self, message): self._log("DEBUG", message)
    def info(self, message): self._log("INFO", message)
    def wait(self, message): self._log("WAIT", message)
    def ok(self, message): self._log("OK", message)
    def warning(self, message): self._log("WARNING", message)
    def error(self, message): self._log("ERROR", message) 