
from collections import defaultdict

from automate.Etat import Etat
from automate.Transition import Transition



class Automate:
    def __init__(self, listAlphabets=None, listEtats=None, listInitiaux=None, listFinaux=None, listTransition=None):
        self.listAlphabets = listAlphabets or []
        self.listEtats = listEtats or []
        self.listInitiaux = listInitiaux or []
        self.listFinaux = listFinaux or []
        self.listTransition = listTransition or []
        self.handlers = defaultdict(list)

    def ajouter_etat(self, etat):
        self.listEtats.append(etat)

    def supprimer_etat(self, idEtat):
        self.listEtats = [etat for etat in self.listEtats if etat.idEtat != idEtat]

    def ajouter_transition(self, transition):
        self.listTransition.append(transition)

    def supprimer_transition(self, idTransition):
        self.listTransition = [t for t in self.listTransition if t.idtransition != idTransition]

    def afficher_graphe(self, master):
        from graphviz import Digraph
        from PIL import Image, ImageTk
        import tkinter as tk

        # Créer un objet Graphviz
        automate = Digraph(format='png')
        automate.attr(rankdir='LR')  # Orientation gauche-droite

        # Ajouter les états initiaux
        for init in self.listInitiaux:
            automate.node(f"start_{init}", label="", shape="point", color="red")
            automate.edge(f"start_{init}", str(init))

        # Ajouter uniquement les états utilisés dans des transitions ou comme initiaux/finals
        for etat in self.listEtats:
            if any(t.etatSource == etat.idEtat or t.etatDestination == etat.idEtat for t in self.listTransition) \
                    or etat.idEtat in self.listInitiaux or etat.idEtat in self.listFinaux:
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

        # Vérifier s'il y a un canvas existant et le supprimer s'il existe
        for widget in master.winfo_children():
            if isinstance(widget, tk.Canvas):
                widget.destroy()

        # Créer un nouveau canvas pour afficher l'image
        canvas = tk.Canvas(master, bg="white")
        canvas.pack(fill=tk.BOTH, expand=True)

        # Calculer les dimensions de l'image
        img_width, img_height = image.size

        # Obtenir les dimensions de la fenêtre
        def update_canvas():
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()

            # Calculer les positions pour centrer l'image
            x_offset = max((canvas_width - img_width) // 2, 0)
            y_offset = max((canvas_height - img_height) // 2, 0)

            # Effacer le canvas et redessiner l'image au centre
            canvas.delete("all")
            canvas.create_image(x_offset, y_offset, anchor="nw", image=photo)

        # Mettre à jour la disposition du canvas à chaque redimensionnement
        canvas.bind("<Configure>", lambda event: update_canvas())

        # Appeler une première fois pour afficher l'image
        update_canvas()

    def determiniser(self):
        etats_deterministes = []
        transitions_deterministes = []
        nouveaux_etats = {}
        compteur_transition = 0  # Pour générer des identifiants uniques pour les transitions

        # Création du nouvel état initial
        initial = frozenset(self.listInitiaux)
        pile = [initial]
        nouveaux_etats[initial] = f"{{{','.join(map(str, initial))}}}"

        while pile:
            etat_actuel = pile.pop()
            etats_deterministes.append(nouveaux_etats[etat_actuel])

            # Regrouper les transitions par symbole
            transitions_par_symbole = {}
            for transition in self.listTransition:
                if transition.etatSource in etat_actuel:
                    for symbole in transition.alphabet.split(','):  # Assurez-vous que `alphabet` est une chaîne
                        if symbole not in transitions_par_symbole:
                            transitions_par_symbole[symbole] = set()
                        transitions_par_symbole[symbole].add(transition.etatDestination)

            # Créer de nouveaux états et transitions
            for symbole, destinations in transitions_par_symbole.items():
                nouvel_etat = frozenset(destinations)
                if nouvel_etat not in nouveaux_etats:
                    nouveaux_etats[nouvel_etat] = f"{{{','.join(map(str, nouvel_etat))}}}"
                    pile.append(nouvel_etat)
                # Créer une nouvelle transition avec un identifiant unique
                transitions_deterministes.append(
                    Transition(
                        idtransition=compteur_transition,  # Identifiant unique
                        etatSource=nouveaux_etats[etat_actuel],
                        etatDestination=nouveaux_etats[nouvel_etat],
                        alphabet=symbole
                    )
                )
                compteur_transition += 1  # Incrémenter le compteur pour le prochain ID

        # Déterminer les états finaux
        etats_finaux = [
            et for et in etats_deterministes
            if any(f in eval(et) for f in self.listFinaux)  # Vérifie si l'état contient un état final
        ]

        # Retourner l'automate déterministe
        return Automate(
            listAlphabets=self.listAlphabets,
            listEtats=[Etat(i, etat) for i, etat in enumerate(etats_deterministes)],
            listInitiaux=[nouveaux_etats[initial]],
            listFinaux=etats_finaux,
            listTransition=transitions_deterministes,
        )

    def est_deterministe(self):
        # Vérifier s'il y a un unique état initial
        if len(self.listInitiaux) != 1:
            return False

        # Vérifier s'il n'y a pas de transitions ambiguës
        transitions_par_etat = defaultdict(set)
        for t in self.listTransition:
            if (t.etatSource, t.alphabet) in transitions_par_etat:
                return False
            transitions_par_etat[(t.etatSource, t.alphabet)] = t.etatDestination

        return True

    def minimiser(self):
        # Étape 1 : Séparer les états en deux groupes : finaux et non-finaux
        groupes = [set(self.listFinaux), set(e.idEtat for e in self.listEtats if e.idEtat not in self.listFinaux)]

        # Étape 2 : Raffiner les groupes
        def trouver_groupe(etat, groupes, alphabet):
            """
            Retourne l'indice du groupe auquel appartient l'état après la transition.
            """
            for i, groupe in enumerate(groupes):
                if etat in groupe:
                    return i
            return -1

        def raffiner_groupes(groupes):
            nouveaux_groupes = []
            for groupe in groupes:
                sous_groupes = defaultdict(set)
                for etat in groupe:
                    signature = tuple(
                        (symbole, trouver_groupe(
                            next((t.etatDestination for t in self.listTransition if
                                  t.etatSource == etat and t.alphabet == symbole), None),
                            groupes, symbole))
                        for symbole in self.listAlphabets
                    )
                    sous_groupes[signature].add(etat)
                nouveaux_groupes.extend(sous_groupes.values())

            # Imprimer les groupes raffinés pour le débogage
            print(f"Groupes raffinés : {nouveaux_groupes}")

            return nouveaux_groupes

        while True:
            # Raffiner les groupes à chaque itération
            nouveaux_groupes = raffiner_groupes(groupes)

            # Si les groupes ne changent pas, on arrête l'itération
            if nouveaux_groupes == groupes:
                break

            # Mettre à jour les groupes pour la prochaine itération
            groupes = nouveaux_groupes

        # Étape 3 : Construire le nouvel automate minimisé
        mapping = {etat: i for i, groupe in enumerate(groupes) for etat in groupe}
        nouveaux_etats = [Etat(idEtat=i, labelEtat=f"État {i}") for i in range(len(groupes))]
        nouveaux_transitions = []

        for t in self.listTransition:
            source = mapping[t.etatSource]
            destination = mapping[t.etatDestination]
            if not any(
                    nt.etatSource == source and nt.etatDestination == destination and nt.alphabet == t.alphabet for nt
                    in nouveaux_transitions):
                nouveaux_transitions.append(
                    Transition(idtransition=len(nouveaux_transitions), etatSource=source, etatDestination=destination,
                               alphabet=t.alphabet)
                )

        etats_initiaux = {mapping[etat] for etat in self.listInitiaux}
        etats_finaux = {mapping[etat] for etat in self.listFinaux}

        return Automate(
            listAlphabets=self.listAlphabets,
            listEtats=nouveaux_etats,
            listInitiaux=list(etats_initiaux),
            listFinaux=list(etats_finaux),
            listTransition=nouveaux_transitions
        )



















