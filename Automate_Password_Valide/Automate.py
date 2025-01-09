class Automate:
    def __init__(self):
        self.etat = "Initial"
        self.transitions = {
            "Initial": self.transition_initial,
            "MajusculeOk": self.transition_majuscule,
            "MinusculeOk": self.transition_minuscule,
            "ChiffreOk": self.transition_chiffre,
            "SpecialOk": self.transition_special,
            "LongueurOk": self.transition_length,
        }
        self.visited = {"Initial"}  # États visités

    def transition_initial(self, char):
        if char.isupper():
            self.etat = "MajusculeOk"
        elif char.islower():
            self.etat = "MinusculeOk"
        elif char.isdigit():
            self.etat = "ChiffreOk"
        elif not char.isalnum():
            self.etat = "SpecialOk"
        self.visited.add(self.etat)

    def transition_majuscule(self, char):
        if char.islower():
            self.etat = "MinusculeOk"
        elif char.isdigit():
            self.etat = "ChiffreOk"
        elif not char.isalnum():
            self.etat = "SpecialOk"
        self.visited.add(self.etat)

    def transition_minuscule(self, char):
        if char.isupper():
            self.etat = "MajusculeOk"
        elif char.isdigit():
            self.etat = "ChiffreOk"
        elif not char.isalnum():
            self.etat = "SpecialOk"
        self.visited.add(self.etat)

    def transition_chiffre(self, char):
        if char.isupper():
            self.etat = "MajusculeOk"
        elif char.islower():
            self.etat = "MinusculeOk"
        elif not char.isalnum():
            self.etat = "SpecialOk"
        self.visited.add(self.etat)

    def transition_special(self, char):
        if char.isupper():
            self.etat = "MajusculeOk"
        elif char.islower():
            self.etat = "MinusculeOk"
        elif char.isdigit():
            self.etat = "ChiffreOk"
        self.visited.add(self.etat)

    def transition_length(self, mot_de_passe):
        if 8 <= len(mot_de_passe) <= 18:
            self.etat = "LongueurOk"
        else:
            self.etat = "Initial"
        self.visited.add(self.etat)

    def verifier_temps_reel(self, mot_de_passe):
        # Réinitialise l'état et les états visités
        self.etat = "Initial"
        self.visited = {"Initial"}

        # Parcourt chaque caractère du mot de passe
        for char in mot_de_passe:
            if self.etat in self.transitions:
                self.transitions[self.etat](char)

        # Vérifie la longueur
        self.transition_length(mot_de_passe)
