class Container:
    def __init__(self, input: str = "", history: list[str] = None, urgency: float = 0.5, freedom: float = 0.5, facts: list[str] = None, instructions: list[str]  = None, personality: list[str]  = None):
        self.input: str = input
        self.history: list[str] = history if history != None else []
        self.urgency: float = urgency
        self.freedom: float = freedom
        self.facts: list[str] = facts if facts != None else []
        self.instructions: list[str] = instructions if instructions != None else []
        self.personality: list[str] = personality if personality != None else []

    def __str__(self):
        return (
            f"Container(\n"
            f"  urgency={self.urgency},\n"
            f"  freedom={self.freedom},\n"
            f"  facts={self.facts},\n"
            f"  instructions={self.instructions},\n"
            f"  personality={self.personality}\n"
            f")"
        )