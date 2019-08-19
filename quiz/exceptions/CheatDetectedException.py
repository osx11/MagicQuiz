class CheatDetectedException(Exception):
    """
    выбрасывается, если пользователь пытается дать ответ на вопрос, на который уже отвечал ранее
    """

    def __init__(self):
        super(CheatDetectedException, self).__init__("Cheat detected")
