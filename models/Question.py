
class Question:
    def __init__(self, *args, **kwargs):
        self.question = kwargs.get('question')
        self.options = kwargs.get('options')
        self.correct_answer = kwargs.get('correct_answer')

    def __str__(self):
        return f"""
                {self.question}
                1. {self.options[0]}
                2. {self.options[1]}
                3. {self.options[2]}
                4. {self.options[3]}
                """

