import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from fpdf import FPDF
from tkinter.font import Font
from Automate import Automate


class RealTimePasswordApp:
    def __init__(self, root):

        self.root = root
        self.root.title("Validez votre mot de passe")
        self.root.geometry("1200x800")
        self.root.config(bg="#f9f9f9")

        self.automate = Automate()
        self.password_logs = []
        self.graph = nx.DiGraph()  # Initialisation du graphe
        self.pos = None  # Position des nœuds
        self.setup_graph()  # Configuration du graphe

        # Styling variables
        self.font_main = Font(family="Arial", size=14)
        self.font_small = Font(family="Arial", size=12)

        # Split the window into two equal panes (50% 50%)
        self.paned_window = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashwidth=5, bg="#f9f9f9")
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Left Pane: User input and criteria
        self.left_pane = tk.Frame(self.paned_window, bg="#f9f9f9", width=600)  # 50% of the window width
        self.paned_window.add(self.left_pane)

        # Right Pane: Graph visualization
        self.right_pane = tk.Frame(self.paned_window, bg="#ffffff", width=600)  # 50% of the window width
        self.paned_window.add(self.right_pane)

        self.create_widgets()

    def setup_graph(self):
        """Initialise et configure le graphe d'automate."""
        self.graph.add_nodes_from(["Initial", "MajusculeOk", "MinusculeOk", "ChiffreOk", "SpecialOk", "LongueurOk"])
        self.graph.add_edges_from([
            ("Initial", "MajusculeOk"),
            ("Initial", "MinusculeOk"),
            ("Initial", "ChiffreOk"),
            ("Initial", "SpecialOk"),
            ("MajusculeOk", "MinusculeOk"),
            ("MinusculeOk", "ChiffreOk"),
            ("ChiffreOk", "SpecialOk"),
            ("SpecialOk", "LongueurOk"),
        ])
        self.pos = nx.spring_layout(self.graph)

    def create_widgets(self):
        """Setup the UI elements in both panes."""
        # Left Pane: Inputs and Criteria
        title_label = tk.Label(
            self.left_pane,
            text="Formulaire d'Inscription",
            font=("Helvetica", 20, "bold"),  # Police 20 avec gras
            fg="#2196F3",  # Couleur du texte en bleu (Hex : Blue 500)
            bg="#f9f9f9"  # Fond blanc cassé, assorti au design existant
        )
        title_label.pack(pady=20)

        # Form Frame
        form_frame = tk.Frame(self.left_pane, bg="#f9f9f9")
        form_frame.pack(pady=20, fill=tk.X)

        # First Name
        tk.Label(
            form_frame, text="Prénom:", font=self.font_main, bg="#f9f9f9"
        ).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.entry_first_name = ttk.Entry(form_frame, font=("Arial", 14), width=30)
        self.entry_first_name.grid(row=0, column=1, padx=10, pady=5)

        # Last Name
        tk.Label(
            form_frame, text="Nom:", font=self.font_main, bg="#f9f9f9"
        ).grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.entry_last_name = ttk.Entry(form_frame, font=("Arial", 14), width=30)
        self.entry_last_name.grid(row=1, column=1, padx=10, pady=5)



        # Email
        tk.Label(
            form_frame, text="Email:", font=self.font_main, bg="#f9f9f9"
        ).grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        self.entry_email = ttk.Entry(form_frame, font=("Arial", 14), width=30)
        self.entry_email.grid(row=3, column=1, padx=10, pady=5)

        # Password Input Section (modifiée pour utiliser grid)
        tk.Label(
            form_frame, text="Mot de passe:",
            font=self.font_main, bg="#f9f9f9", anchor="w"
        ).grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)  # Texte aligné à gauche

        # Entry field for password
        self.entry_password = ttk.Entry(form_frame, font=("Arial", 14), width=30, show="•")
        self.entry_password.grid(row=4, column=1, padx=10, pady=5)  # Aligné à droite du label
        self.entry_password.bind("<KeyRelease>", self.on_key_release)

        # Button to toggle password visibility
        self.password_visible = False
        self.toggle_button = tk.Label(
            form_frame, text="👁️", font=("Arial", 16), bg="#f9f9f9", cursor="hand2"
        )
        self.toggle_button.grid(row=4, column=2, padx=10, pady=5)  # Bouton à droite de l'entrée
        self.toggle_button.bind("<Button-1>", self.toggle_password_visibility)

        # Criteria Feedback
        criteria_frame = tk.Frame(self.left_pane, bg="#f9f9f9")
        criteria_frame.pack(pady=20, fill=tk.X)

        self.criteria_labels = {
            "uppercase": self.create_criteria_row(criteria_frame, "Au moins une majuscule (A-Z)"),
            "lowercase": self.create_criteria_row(criteria_frame, "Au moins une minuscule (a-z)"),
            "digit": self.create_criteria_row(criteria_frame, "Au moins un chiffre (0-9)"),
            "special": self.create_criteria_row(criteria_frame, "Au moins un caractère spécial (!@#&)"),
            "length": self.create_criteria_row(criteria_frame, "Longueur entre 8 et 18 caractères"),
        }

        # Result Section
        self.security_label = tk.Label(
            self.left_pane, text="Niveau de sécurité : Inconnu",
            font=("Helvetica", 16, "bold"), fg="#FF5733", bg="#f9f9f9"
        )
        self.security_label.pack(pady=10)

        report_button = tk.Button(
            self.left_pane, text="Générer le Rapport", command=self.generate_pdf_report,
            font=("Helvetica", 14, "bold"), bg="#2196F3", fg="white",
            activebackground="#2196F3", activeforeground="white", bd=0, padx=10, pady=5
        )
        report_button.pack(pady=10)

        # Right Pane: Graph
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_pane)
        self.canvas.get_tk_widget().pack(pady=20, fill=tk.BOTH, expand=True)

    def toggle_password_visibility(self, event=None):
        """Toggle the visibility of the password."""
        if self.password_visible:
            self.entry_password.config(show="•")
            self.toggle_button.config(text="👁️")
        else:
            self.entry_password.config(show="")
            self.toggle_button.config(text="👁️‍🗨️")
        self.password_visible = not self.password_visible

    def create_criteria_row(self, parent, text):
        """Create a row in the criteria section with an indicator and a label."""
        frame = tk.Frame(parent, bg="#f9f9f9")
        frame.pack(anchor="w", padx=20, pady=5)

        indicator = tk.Label(frame, text="✗", font=("Arial", 16), fg="red", bg="#f9f9f9")
        indicator.pack(side="left", padx=5)

        label = tk.Label(frame, text=text, font=self.font_small, bg="#f9f9f9")
        label.pack(side="left")

        return indicator

    def on_key_release(self, event):
        """Handle the key release event for real-time validation."""
        password = self.entry_password.get()
        self.automate.verifier_temps_reel(password)

        # Capture transitions and their validity
        transitions_status = []
        for state in self.automate.visited:
            if state.endswith("Ok"):
                transitions_status.append((state, "Valide"))
            else:
                transitions_status.append((state, "Non Valide"))

        self.password_logs.append({
            "password": password,
            "transitions": transitions_status
        })

        self.update_criteria_feedback(password)
        self.update_graph()

    def update_criteria_feedback(self, password):
        """Update criteria indicators and labels based on the password."""
        conditions = {
            "uppercase": "MajusculeOk" in self.automate.visited,
            "lowercase": "MinusculeOk" in self.automate.visited,
            "digit": "ChiffreOk" in self.automate.visited,
            "special": "SpecialOk" in self.automate.visited,
            "length": 8 <= len(password) <= 18,
        }

        valid_conditions = sum(conditions.values())

        for key, indicator in self.criteria_labels.items():
            if conditions[key]:
                indicator.config(text="✓", fg="green")
            else:
                indicator.config(text="✗", fg="red")

        if valid_conditions == 5:
            self.security_label.config(text="Niveau de sécurité : Fort", fg="green")
        elif valid_conditions >= 3:
            self.security_label.config(text="Niveau de sécurité : Moyen", fg="#FF9800")
        else:
            self.security_label.config(text="Niveau de sécurité : Faible", fg="#FF5733")

    def update_graph(self):
        """Visualize the current graph."""
        self.ax.clear()

        node_colors = ["green" if n in self.automate.visited else "red" for n in self.graph.nodes]
        edge_colors = ["green" if v in self.automate.visited else "red" for u, v in self.graph.edges]

        nx.draw(
            self.graph, pos=self.pos, with_labels=True, ax=self.ax,
            node_color=node_colors, node_size=3000, font_size=10, font_color="white",
            edge_color=edge_colors, width=2, font_weight="bold"
        )

        self.canvas.draw()

    def generate_pdf_report(self):
        """Generate the password validation report in PDF format."""
        if not self.password_logs:
            messagebox.showwarning("Aucun mot de passe", "Aucun mot de passe n'a été validé.")
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="Rapport de Validation des Mots de Passe", ln=True, align="C")
        pdf.ln(10)

        for log in self.password_logs:
            pdf.cell(200, 10, txt=f"Mot de passe: {log['password']}", ln=True)

            pdf.cell(200, 10, txt="Transitions :", ln=True)
            for transition, status in log['transitions']:
                pdf.cell(200, 10, txt=f"  {transition}: {status}", ln=True)

            pdf.ln(5)

        pdf.output("rapport_validation.pdf")
        messagebox.showinfo("Rapport Généré", "Le rapport PDF a été généré avec succès.")


if __name__ == "__main__":
    root = tk.Tk()
    app = RealTimePasswordApp(root)
    root.mainloop()