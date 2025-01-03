class Transition:
    def __init__(self, idtransition, etatSource, etatDestination, alphabet):
        self.idtransition = idtransition
        self.etatSource = etatSource
        self.etatDestination = etatDestination
        self.alphabet = alphabet

    def get_transition(self):
        return (self.etatSource, self.alphabet, self.etatDestination)
