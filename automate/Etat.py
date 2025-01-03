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
# Méthodes pour vérifier si l'état est initial ou final
    def est_initial(self):
        return self.typeEtat == 'initial'

    def est_final(self):
        return self.typeEtat == 'final'

    # Méthode pour afficher un état de manière lisible
    def __repr__(self):
        return f"Etat(id={self.idEtat}, label={self.labelEtat}, type={self.typeEtat})"

    def __str__(self):
        return f"État {self.idEtat} - {self.labelEtat} ({'Initial' if self.est_initial() else 'Final' if self.est_final() else 'Normal'})"