class Etat:
    def __init__(self, idEtat, labelEtat, typeEtat=None):
        self.idEtat = idEtat
        self.labelEtat = labelEtat
        self.typeEtat = typeEtat  # 'initial', 'final' ou None

    # Getters et setters
    def get_id(self):
        return self.idEtat

    def set_id(self, idEtat):
        self.idEtat = idEtat

    def get_label(self):
        return self.labelEtat

    def set_label(self, labelEtat):
        self.labelEtat = labelEtat

    def get_type(self):
        return self.typeEtat

    def set_type(self, typeEtat):
        self.typeEtat = typeEtat


