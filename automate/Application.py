
from itertools import chain
import tkinter as tk
from tkinter import simpledialog, messagebox
from graphviz import Digraph
from PIL import Image, ImageTk  # Pour afficher les images dans Tkinter
from automate.Alphabet import Alphabet
from .Automate import Automate
from automate.Etat import Etat
from automate.Transition import Transition

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Automate Finite State Machine")
        self.geometry("800x600")

        # Initialisation de l'automate
        self.automate = Automate(
            listEtats=[Etat(i, f"État {i}") for i in [1, 2, 3, 4, 5, 6]],
            listInitiaux=[1, 3, 6],
            listFinaux=[6],
            listTransition=[
                Transition(1, 1, 2, 'a'),
                Transition(2, 1, 4, 'a'),
                Transition(3, 2, 2, 'a'),
                Transition(4, 2, 5, 'c,d'),
                Transition(6, 3, 2, 'b'),
                Transition(7, 3, 4, 'b'),
                Transition(8, 4, 4, 'b'),
                Transition(9, 4, 5, 'c,d'),
                Transition(11, 5, 6, 'e'),
            ]
        )

        # Afficher le graphe initial
        self.automate.afficher_graphe(self)

        # Configuration du menu
        self.config(menu=self.create_menu())

    def create_menu(self):
        # Création de la barre de menu
        menubar = tk.Menu(self)

        # Menu pour gérer les États
        etat_menu = tk.Menu(menubar, tearoff=0)
        etat_menu.add_command(label="Ajouter État", command=self.ajouter_etat)
        etat_menu.add_command(label="Supprimer État", command=self.supprimer_etat)
        etat_menu.add_command(label="Modifier État", command=self.modifier_etat)
        menubar.add_cascade(label="État", menu=etat_menu)

        # Menu pour gérer les Transitions
        transition_menu = tk.Menu(menubar, tearoff=0)
        transition_menu.add_command(label="Ajouter Transition", command=self.ajouter_transition)
        transition_menu.add_command(label="Supprimer Transition", command=self.supprimer_transition)
        transition_menu.add_command(label="Modifier Transition", command=self.modifier_transition)
        menubar.add_cascade(label="Transition", menu=transition_menu)

        # Menu pour les opérations sur l'automate
        operation_menu = tk.Menu(menubar, tearoff=0)
        operation_menu.add_command(label="Déterminiser", command=self.convertir_deterministe)
        operation_menu.add_command(label="Compléter", command=self.completer_automate)  # Nouvelle option pour compléter
        operation_menu.add_command(label="Minimisée", command=self.minimiser_automate)  # Nouveau menu

        operation_menu.add_command(label="Supprimer tout", command=self.supprimer_automate)  # Nouveau menu

        menubar.add_cascade(label="Opérations", menu=operation_menu)

        return menubar



    def ajouter_etat(self):
        # Fenêtre pour entrer les informations de l'état
        formulaire = tk.Toplevel(self)
        formulaire.title("Ajouter un État")
        formulaire.geometry("300x200")
        formulaire.grab_set()  # Rendre la fenêtre modale

        # Champ pour entrer l'ID de l'état
        tk.Label(formulaire, text="ID de l'État:").pack(pady=5)
        id_entry = tk.Entry(formulaire)
        id_entry.pack(pady=5)

        # Options pour sélectionner le type d'état
        initial_var = tk.BooleanVar()
        final_var = tk.BooleanVar()
        tk.Checkbutton(formulaire, text="Initial", variable=initial_var).pack(pady=5)
        tk.Checkbutton(formulaire, text="Final", variable=final_var).pack(pady=5)

        def valider():
            # Récupérer les valeurs du formulaire
            try:
                id_etat = int(id_entry.get())
            except ValueError:
                messagebox.showwarning("Erreur", "L'ID doit être un nombre entier.")
                return

            if any(etat.idEtat == id_etat for etat in self.automate.listEtats):
                messagebox.showwarning("Échec", f"L'état {id_etat} existe déjà.")
            else:
                is_initial = initial_var.get()
                is_final = final_var.get()
                # Ajouter l'état
                self.automate.ajouter_etat(Etat(id_etat, f"État {id_etat}"))
                if is_initial:
                    self.automate.listInitiaux.append(id_etat)
                if is_final:
                    self.automate.listFinaux.append(id_etat)
                messagebox.showinfo("Succès", f"L'état {id_etat} a été ajouté.")
                self.refresh_graph()
                formulaire.destroy()

        # Boutons Valider/Annuler
        bouton_frame = tk.Frame(formulaire)
        bouton_frame.pack(pady=10)
        tk.Button(bouton_frame, text="Valider", command=valider).pack(side=tk.LEFT, padx=10)
        tk.Button(bouton_frame, text="Annuler", command=formulaire.destroy).pack(side=tk.RIGHT, padx=10)

    def supprimer_etat(self):
        id_etat = simpledialog.askinteger("Supprimer État", "Entrez l'ID de l'état à supprimer:")
        if id_etat:
            self.automate.supprimer_etat(id_etat)
            messagebox.showinfo("Succès", f"L'état {id_etat} a été supprimé.")
            self.refresh_graph()

    def modifier_etat(self):
        id_etat = simpledialog.askinteger("Modifier État", "Entrez l'ID de l'état à modifier:")
        if id_etat:
            nouveau_nom = simpledialog.askstring("Modifier État", "Entrez le nouveau nom de l'état:")
            for etat in self.automate.listEtats:
                if etat.idEtat == id_etat:
                    etat.nom = nouveau_nom
                    messagebox.showinfo("Succès", f"L'état {id_etat} a été renommé en {nouveau_nom}.")
                    self.refresh_graph()
                    return
            messagebox.showwarning("Erreur", f"L'état {id_etat} n'existe pas.")

    # Méthodes pour gérer les transitions
    def ajouter_transition(self):
        # Création de la fenêtre de dialogue
        form = tk.Toplevel(self)
        form.title("Ajouter Transition")
        form.geometry("300x200")
        form.grab_set()  # Rendre la fenêtre modale

        # Widgets du formulaire
        tk.Label(form, text="État Source:").grid(row=0, column=0, padx=10, pady=10)
        source_entry = tk.Entry(form)
        source_entry.grid(row=0, column=1)

        tk.Label(form, text="État Destination:").grid(row=1, column=0, padx=10, pady=10)
        destination_entry = tk.Entry(form)
        destination_entry.grid(row=1, column=1)

        tk.Label(form, text="Alphabet:").grid(row=2, column=0, padx=10, pady=10)
        alphabet_entry = tk.Entry(form)
        alphabet_entry.grid(row=2, column=1)

        def valider():
            try:
                source = int(source_entry.get())
                destination = int(destination_entry.get())
                alphabet = alphabet_entry.get()
                if not alphabet:
                    raise ValueError("Alphabet ne peut pas être vide.")
                # Génération automatique de l'ID de transition
                id_transition = max((t.idtransition for t in self.automate.listTransition), default=0) + 1
                self.automate.ajouter_transition(Transition(id_transition, source, destination, alphabet))
                messagebox.showinfo("Succès", f"Transition {id_transition} ajoutée.")
                self.refresh_graph()
                form.destroy()
            except ValueError as e:
                messagebox.showerror("Erreur", f"Entrée invalide : {e}")

        # Boutons pour valider ou annuler
        tk.Button(form, text="Valider", command=valider).grid(row=3, column=0, padx=10, pady=10)
        tk.Button(form, text="Annuler", command=form.destroy).grid(row=3, column=1, padx=10, pady=10)

    def supprimer_transition(self):
        id_transition = simpledialog.askinteger("Supprimer Transition", "Entrez l'ID de la transition à supprimer:")
        if id_transition:
            self.automate.supprimer_transition(id_transition)
            messagebox.showinfo("Succès", f"La transition {id_transition} a été supprimée.")
            self.refresh_graph()

    def modifier_transition(self):
        # Demander l'ID de la transition à modifier
        id_transition = simpledialog.askinteger("Modifier Transition", "Entrez l'ID de la transition à modifier:")
        if not id_transition:
            return

        # Rechercher la transition correspondante
        transition = next((t for t in self.automate.listTransition if t.idtransition == id_transition), None)
        if not transition:
            messagebox.showwarning("Erreur", f"La transition {id_transition} n'existe pas.")
            return

        # Création de la fenêtre de modification
        form = tk.Toplevel(self)
        form.title(f"Modifier Transition {id_transition}")
        form.geometry("300x200")
        form.grab_set()  # Rendre la fenêtre modale

        # Widgets du formulaire
        tk.Label(form, text="État Source:").grid(row=0, column=0, padx=10, pady=10)
        source_entry = tk.Entry(form)
        source_entry.insert(0, transition.etatSource)  # Pré-remplir avec la valeur actuelle
        source_entry.grid(row=0, column=1)

        tk.Label(form, text="État Destination:").grid(row=1, column=0, padx=10, pady=10)
        destination_entry = tk.Entry(form)
        destination_entry.insert(0, transition.etatDestination)  # Pré-remplir avec la valeur actuelle
        destination_entry.grid(row=1, column=1)

        tk.Label(form, text="Alphabet:").grid(row=2, column=0, padx=10, pady=10)
        alphabet_entry = tk.Entry(form)
        alphabet_entry.insert(0, transition.alphabet)  # Pré-remplir avec la valeur actuelle
        alphabet_entry.grid(row=2, column=1)

        def valider():
            try:
                nouvelle_source = int(source_entry.get())
                nouvelle_destination = int(destination_entry.get())
                nouvel_alphabet = alphabet_entry.get()
                if not nouvel_alphabet:
                    raise ValueError("Alphabet ne peut pas être vide.")

                # Mise à jour de la transition
                transition.etatSource = nouvelle_source
                transition.etatDestination = nouvelle_destination
                transition.alphabet = nouvel_alphabet
                messagebox.showinfo("Succès", f"Transition {id_transition} modifiée.")
                self.refresh_graph()
                form.destroy()
            except ValueError as e:
                messagebox.showerror("Erreur", f"Entrée invalide : {e}")

        # Boutons pour valider ou annuler
        tk.Button(form, text="Valider", command=valider).grid(row=3, column=0, padx=10, pady=10)
        tk.Button(form, text="Annuler", command=form.destroy).grid(row=3, column=1, padx=10, pady=10)

    # Méthode pour rafraîchir le graphe
    def refresh_graph(self):
        for widget in self.winfo_children():
            if isinstance(widget, tk.Label):
                widget.destroy()
        self.automate.afficher_graphe(self)









    def supprimer_automate(self):
        """
        Supprime tout l'automate, réinitialisant les états, transitions, et autres composants.
        """
        self.automate.listEtats = []
        self.automate.listInitiaux = []
        self.automate.listFinaux = []
        self.automate.listTransition = []

        # Rafraîchir l'affichage pour refléter l'automate vide
        messagebox.showinfo("Succès", "L'automate a été supprimé.")
        self.refresh_graph()







    def completer_automate(self):
        """
        Complète un automate en ajoutant un état "poubelle" et des transitions manquantes.
        """
        # Ajout de l'état poubelle si nécessaire
        id_poubelle = max((etat.idEtat for etat in self.automate.listEtats), default=0) + 1
        etat_poubelle = Etat(id_poubelle, "Poubelle")
        self.automate.ajouter_etat(etat_poubelle)

        # Parcourir les états et l'alphabet pour compléter les transitions
        for etat in self.automate.listEtats:
            for symbole in self.automate.get_alphabet():
                if not any(
                        t.etatSource == etat.idEtat and symbole in t.alphabet.split(',')
                        for t in self.automate.listTransition
                ):
                    # Ajouter une transition vers l'état poubelle
                    id_transition = max((t.idtransition for t in self.automate.listTransition), default=0) + 1
                    self.automate.ajouter_transition(Transition(
                        idtransition=id_transition,
                        etatSource=etat.idEtat,
                        etatDestination=id_poubelle,
                        alphabet=symbole
                    ))

        messagebox.showinfo("Succès", "L'automate a été complété avec succès.")
        self.refresh_graph()

    def completer_automate(self):
        """
        Complète un automate en ajoutant un état "poubelle" et des transitions manquantes.
        """
        # Identifier l'alphabet de l'automate
        alphabet = set(chain.from_iterable(
            transition.alphabet.split(',') for transition in self.automate.listTransition
        ))

        # Ajouter un état "poubelle" s'il n'existe pas
        id_poubelle = max((etat.idEtat for etat in self.automate.listEtats), default=0) + 1
        etat_poubelle = Etat(id_poubelle, "Poubelle")
        self.automate.ajouter_etat(etat_poubelle)

        # Parcourir chaque état et chaque symbole de l'alphabet
        for etat in self.automate.listEtats:
            for symbole in alphabet:
                # Vérifier si une transition existe pour cet état et ce symbole
                if not any(
                        t.etatSource == etat.idEtat and symbole in t.alphabet.split(',')
                        for t in self.automate.listTransition
                ):
                    # Ajouter une transition vers l'état "poubelle"
                    id_transition = max((t.idtransition for t in self.automate.listTransition), default=0) + 1
                    self.automate.ajouter_transition(Transition(
                        idtransition=id_transition,
                        etatSource=etat.idEtat,
                        etatDestination=etat_poubelle.idEtat,
                        alphabet=symbole
                    ))

        # Informer l'utilisateur que l'automate a été complété
        messagebox.showinfo("Succès", "L'automate a été complété avec succès.")
        self.refresh_graph()

    def charger_automate(self, automate):
        """Méthode pour charger un automate dans l'application"""
        self.automate = automate

    def verifier_determinisme(self):
        """Vérifie si l'automate est déterministe"""
        if self.automate is None:
            messagebox.showerror("Erreur", "Aucun automate chargé.")
            return
        if self.automate.est_deterministe():
            messagebox.showinfo("Résultat", "L'automate est déterministe.")
        else:
            messagebox.showinfo("Résultat", "L'automate n'est pas déterministe.")

    def convertir_deterministe(self):
        """Convertit l'automate non déterministe en déterministe et affiche le résultat"""
        if self.automate is None:
            messagebox.showerror("Erreur", "Aucun automate chargé.")
            return
        automate_d = self.automate.convertir_en_deterministe()
        if automate_d.est_deterministe():
            messagebox.showinfo("Conversion", "L'automate a été converti en déterministe.")
        else:
            messagebox.showinfo("Conversion", "La conversion a échoué.")

    def minimiser_automate(self):
        """Minimise un automate déterministe en utilisant la méthode de Moore."""
        if self.automate is None:
            messagebox.showerror("Erreur", "Aucun automate chargé.")
            return

        if not self.automate.est_deterministe():
            messagebox.showerror("Erreur", "L'automate n'est pas déterministe.")
            return

        # Code pour minimiser l'automate
        self.automate.minimiser()
        messagebox.showinfo("Succès", "L'automate a été minimisé.")





    def partitionner_par_transition(self, partitions):
        """
        Partitionne les états en fonction de leurs transitions.
        """
        nouvelles_partitions = []
        # Exemple de partitionnement par transitions (à adapter selon l'implémentation)
        for partition in partitions:
            # Partitionner chaque groupe en fonction des transitions
            transitions_par_ensemble = {}
            for etat in partition:
                cle = tuple(sorted([transition.etatDestination for transition in self.automate.listTransition if
                                    transition.etatSource == etat.idEtat]))
                if cle not in transitions_par_ensemble:
                    transitions_par_ensemble[cle] = []
                transitions_par_ensemble[cle].append(etat)

            nouvelles_partitions.extend(transitions_par_ensemble.values())

        return nouvelles_partitions

    def fusionner_etats_equivalents(self, partitions):
        """
        Fusionne les états équivalents en un seul état pour chaque partition.
        """
        nouveaux_etats = []
        for partition in partitions:
            # Créer un nouvel état qui représente l'ensemble de la partition
            # Par exemple, prendre le premier état de la partition pour le nom
            nouvel_etat = Etat(max([etat.idEtat for etat in partition]), f"État Fusionné")
            nouveaux_etats.append(nouvel_etat)
            # Mettre à jour les transitions en conséquence
            for etat in partition:
                # Les transitions doivent pointer vers l'état fusionné
                for transition in self.automate.listTransition:
                    if transition.etatSource == etat.idEtat:
                        transition.etatSource = nouvel_etat.idEtat

        # Mettre à jour l'automate avec les nouveaux états fusionnés
        self.automate.listEtats = nouveaux_etats
        self.automate.listInitiaux = [etat.idEtat for etat in nouveaux_etats if
                                      etat.idEtat in self.automate.listInitiaux]
        self.automate.listFinaux = [etat.idEtat for etat in nouveaux_etats if etat.idEtat in self.automate.listFinaux]

