import tkinter as tk
from tkinter import simpledialog, messagebox
from graphviz import Digraph
from PIL import Image, ImageTk  # Pour afficher les images dans Tkinter
from automate.Alphabet import Alphabet
from automate.Etat import Etat
from automate.Transition import Transition

class Automate:
    def __init__(self, listAlphabets=None, listEtats=None, listInitiaux=None, listFinaux=None, listTransition=None):
        self.listAlphabets = listAlphabets or []
        self.listEtats = listEtats or []
        self.listInitiaux = listInitiaux or []
        self.listFinaux = listFinaux or []
        self.listTransition = listTransition or []

    def ajouter_etat(self, etat):
        self.listEtats.append(etat)

    def supprimer_etat(self, idEtat):
        self.listEtats = [etat for etat in self.listEtats if etat.idEtat != idEtat]

    def ajouter_transition(self, transition):
        self.listTransition.append(transition)

    def supprimer_transition(self, idTransition):
        self.listTransition = [t for t in self.listTransition if t.idtransition != idTransition]

    def afficher_graphe(self, master):
        # Créer un objet Graphviz
        automate = Digraph(format='png')
        automate.attr(rankdir='LR')  # Orientation gauche-droite

        # Ajouter les états initiaux
        for init in self.listInitiaux:
            automate.node(f"start_{init}", label="", shape="point", color="red")
            automate.edge(f"start_{init}", str(init))

        # Ajouter les états
        for etat in self.listEtats:
            shape = "doublecircle" if etat.idEtat in self.listFinaux else "circle"
            automate.node(str(etat.idEtat), label=f"État {etat.idEtat}", shape=shape)

        # Ajouter les transitions
        for t in self.listTransition:
            automate.edge(str(t.etatSource), str(t.etatDestination), label=t.alphabet)

        # Sauvegarder l'image générée
        automate.render("automate", cleanup=True)

        # Charger l'image PNG générée
        image = Image.open("automate.png")
        photo = ImageTk.PhotoImage(image)

        # Créer un widget Label pour afficher l'image dans Tkinter
        label = tk.Label(master, image=photo)
        label.image = photo  # Garder une référence à l'image pour éviter qu'elle ne soit collectée par le garbage collector
        label.pack()

    def est_deterministe(self):
        """
        Vérifie si l'automate est déterministe.
        Un automate est déterministe si, pour chaque état et chaque symbole,
        il y a au plus une transition sortante.
        """
        for etat in self.listEtats:
            if etat in self.listTransition:
                for symbole in self.listTransition[etat]:  # Accès direct aux clés du dictionnaire
                    # Si un état a plus d'une transition pour le même symbole, l'automate n'est pas déterministe
                    if len(self.listTransition[etat][symbole]) > 1:
                        return False
        return True

    def convertir_en_deterministe(self):
        """
        Convertit un automate non déterministe en un automate déterministe.
        """
        # Création du nouvel automate déterministe
        new_etats = []
        new_initiaux = [tuple(self.listInitiaux)]  # L'état initial est un tuple des états initiaux
        new_transitions = {}
        new_finaux = []

        # Pile des nouveaux sous-états à traiter
        pile = [tuple(self.listInitiaux)]

        # Créer un mapping entre les ensembles d'états et les nouveaux états
        ensemble_to_etat = {tuple(self.listInitiaux): 0}
        new_etats.append(tuple(self.listInitiaux))

        # Algorithme de déterminisation (Powerset)
        while pile:
            current_ensemble = pile.pop()

            # Si cet ensemble d'états contient un état final, il devient un état final dans le nouvel automate
            if any(etat in self.listFinaux for etat in current_ensemble):
                new_finaux.append(current_ensemble)

            # Construire les transitions pour cet ensemble d'états
            new_transitions[current_ensemble] = {}
            for symbole in self.listAlphabets:  # Pour chaque symbole de l'alphabet
                next_ensemble = set()
                for etat in current_ensemble:
                    # Recherche des transitions correspondantes dans listTransition
                    for transition in self.listTransition:
                        if transition.etatSource == etat and transition.alphabet == symbole:
                            next_ensemble.add(transition.etatDestination)

                next_ensemble = tuple(sorted(next_ensemble))  # Trie pour maintenir l'unicité

                if next_ensemble and next_ensemble not in ensemble_to_etat:
                    # Ajouter l'ensemble des états dans la pile et les nouveaux états
                    ensemble_to_etat[next_ensemble] = len(new_etats)
                    new_etats.append(next_ensemble)
                    pile.append(next_ensemble)

                # Ajouter la transition dans la table des transitions
                new_transitions[current_ensemble][symbole] = next_ensemble

        # Créer l'automate déterministe
        return Automate(listEtats=list(range(len(new_etats))),
                        listInitiaux=[0],
                        listFinaux=[new_etats.index(f) for f in new_finaux],
                        listTransition=new_transitions)

    def minimiser(self):
        """
        Minimise l'automate en utilisant l'algorithme de Moore.
        """
        # 1. Initialiser les partitions de l'automate
        P = []  # P représente les partitions d'états
        non_finaux = [etat for etat in self.listEtats if not etat.est_final()]
        finaux = [etat for etat in self.listEtats if etat.est_final()]

        # Partition initiale : états finaux et non-finaux
        P.append(non_finaux)
        P.append(finaux)

        # 2. Affiner les partitions jusqu'à ce que l'automate soit stable
        stable = False
        while not stable:
            stable = True
            nouvelles_partitions = []

            for partition in P:
                # Regrouper les états ayant les mêmes transitions pour chaque symbole de l'alphabet
                groupes = {}
                for etat in partition:
                    # Obtenir les transitions de l'état actuel
                    transitions = {}
                    for alphabet in self.listAlphabets:
                        transition_etat = self.get_next_state(etat, alphabet)
                        transitions[alphabet] = transition_etat

                    # Utiliser les transitions comme clé pour regrouper les états
                    transitions_tuple = tuple(transitions[alphabet] for alphabet in self.listAlphabets)
                    if transitions_tuple not in groupes:
                        groupes[transitions_tuple] = []
                    groupes[transitions_tuple].append(etat)

                # Créer les nouvelles partitions à partir des groupes
                for groupe in groupes.values():
                    nouvelles_partitions.append(groupe)

            # Si les nouvelles partitions sont différentes, l'automate n'est pas encore stable
            if len(nouvelles_partitions) != len(P):
                stable = False
                P = nouvelles_partitions
            else:
                stable = True

        # 3. Fusionner les états dans les partitions finales
        self.fusionner_etats(P)

    def get_next_state(self, etat, alphabet):
        """
        Retourne l'état suivant à partir d'un état et d'un symbole de l'alphabet.
        """
        for transition in self.listTransition:
            if transition.etatSource == etat.idEtat and transition.alphabet == alphabet:
                return transition.etatDestination
        return None

    def fusionner_etats(self, partitions):
        """
        Fusionne les états dans les partitions données et met à jour l'automate.
        """
        etats_fusionnes = []
        for partition in partitions:
            # Prendre un état de chaque partition comme représentant
            representant = partition[0]
            for etat in partition[1:]:
                # Supprimer les autres états et transitions associés
                self.supprimer_etat(etat.idEtat)

            # Mettre à jour les transitions pour pointer vers le représentant
            for transition in self.listTransition:
                if transition.etatSource in [etat.idEtat for etat in partition]:
                    transition.etatSource = representant.idEtat
                if transition.etatDestination in [etat.idEtat for etat in partition]:
                    transition.etatDestination = representant.idEtat

        # Réorganiser la liste des états
        self.listEtats = [partition[0] for partition in partitions]

        # Mettre à jour les états finaux et initiaux après fusion
        self.listInitiaux = [representant for representant in self.listEtats if representant.est_initial()]
        self.listFinaux = [representant for representant in self.listEtats if representant.est_final()]









