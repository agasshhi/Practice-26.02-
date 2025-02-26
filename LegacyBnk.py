import tkinter as tk
from tkinter import messagebox, simpledialog


# --- Data Model ---

class Client:
    def __init__(self, name):
        self.name = name
        self.accounts = {}  # account_id -> balance

    def add_account(self, account_id, balance=0.0):
        self.accounts[account_id] = balance


class Bank:
    def __init__(self):
        self.clients = {}  # client name -> Client object

    def add_client(self, name):
        if name in self.clients:
            return False
        self.clients[name] = Client(name)
        return True

    def modify_client(self, old_name, new_name):
        if old_name not in self.clients or new_name in self.clients:
            return False
        client_obj = self.clients.pop(old_name)
        client_obj.name = new_name
        self.clients[new_name] = client_obj
        return True

    def delete_client(self, name):
        if name in self.clients:
            del self.clients[name]
            return True
        return False

    def get_client(self, name):
        return self.clients.get(name)


# Global bank instance
bank = Bank()


# --- GUI Application ---

class BankingGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Legacy Banked System")
        self.geometry("500x400")
        self.current_role = None
        self.current_client_name = None  # Only used for client role
        self.active_frame = None  # Reference to current frame for easy logout
        self.create_login_frame()

    def create_login_frame(self):
        """Initial login frame to select a role."""
        self.active_frame = tk.Frame(self)
        self.active_frame.pack(pady=20)

        tk.Label(self.active_frame, text="Select Role", font=("Arial", 14)).pack(pady=5)
        self.role_var = tk.StringVar(value="client")
        tk.Radiobutton(self.active_frame, text="Client", variable=self.role_var, value="client").pack()
        tk.Radiobutton(self.active_frame, text="Super", variable=self.role_var, value="super").pack()
        tk.Radiobutton(self.active_frame, text="Admin", variable=self.role_var, value="admin").pack()

        tk.Button(self.active_frame, text="Login", command=self.login, width=10).pack(pady=10)

    def login(self):
        """Switch to the appropriate dashboard based on selected role."""
        self.current_role = self.role_var.get()
        self.active_frame.destroy()  # remove login frame
        if self.current_role == "client":
            self.prompt_client_name()
            self.create_client_frame()
        elif self.current_role == "super":
            self.create_super_frame()
        else:  # admin
            self.create_admin_frame()

    def prompt_client_name(self):
        """For client role, ask for the client name (and register if new)."""
        name = simpledialog.askstring("Client Login", "Enter your client name:")
        if name:
            self.current_client_name = name
            if not bank.get_client(name):
                bank.add_client(name)
                messagebox.showinfo("Registration", f"Client '{name}' registered successfully.")
        else:
            messagebox.showerror("Error", "Client name is required.")
            self.destroy()

    def logout(self):
        """Log out and return to the login screen."""
        self.active_frame.destroy()
        self.current_role = None
        self.current_client_name = None
        self.create_login_frame()

    # --- Client Dashboard ---
    def create_client_frame(self):
        self.active_frame = tk.Frame(self)
        self.active_frame.pack(pady=10)
        tk.Label(self.active_frame, text=f"Client Dashboard - {self.current_client_name}", font=("Arial", 14)).pack(
            pady=5)

        tk.Button(self.active_frame, text="Add Account", command=self.client_add_account, width=20).pack(pady=5)
        tk.Button(self.active_frame, text="Query Balance", command=self.client_query_balance, width=20).pack(pady=5)
        tk.Button(self.active_frame, text="Back", command=self.logout, width=20).pack(pady=5)

    def client_add_account(self):
        client = bank.get_client(self.current_client_name)
        if not client:
            messagebox.showerror("Error", "Client not found.")
            return
        account_id = simpledialog.askstring("Add Account", "Enter account ID:")
        if account_id:
            balance_str = simpledialog.askstring("Add Account", "Enter initial balance (default 0):")
            try:
                balance = float(balance_str) if balance_str else 0.0
            except ValueError:
                balance = 0.0
            client.add_account(account_id, balance)
            messagebox.showinfo("Success", f"Account '{account_id}' added with balance ${balance}.")

    def client_query_balance(self):
        client = bank.get_client(self.current_client_name)
        if not client:
            messagebox.showerror("Error", "Client not found.")
            return
        account_id = simpledialog.askstring("Query Balance", "Enter account ID:")
        if account_id:
            if account_id in client.accounts:
                balance = client.accounts[account_id]
                messagebox.showinfo("Balance", f"Account '{account_id}' balance: ${balance}.")
            else:
                messagebox.showerror("Error", f"Account '{account_id}' not found.")

    # --- Super Dashboard ---
    def create_super_frame(self):
        self.active_frame = tk.Frame(self)
        self.active_frame.pack(pady=10)
        tk.Label(self.active_frame, text="Super User Dashboard", font=("Arial", 14)).pack(pady=5)

        tk.Button(self.active_frame, text="Modify Client", command=self.modify_client, width=20).pack(pady=5)
        tk.Button(self.active_frame, text="Delete Client", command=self.delete_client, width=20).pack(pady=5)
        tk.Button(self.active_frame, text="Back", command=self.logout, width=20).pack(pady=5)

    def modify_client(self):
        old_name = simpledialog.askstring("Modify Client", "Enter current client name:")
        if old_name:
            new_name = simpledialog.askstring("Modify Client", "Enter new client name:")
            if new_name:
                if bank.modify_client(old_name, new_name):
                    messagebox.showinfo("Success", f"Client '{old_name}' changed to '{new_name}'.")
                else:
                    messagebox.showerror("Error",
                                         "Modification failed. Check if the client exists or if the new name is already used.")

    def delete_client(self):
        name = simpledialog.askstring("Delete Client", "Enter client name to delete:")
        if name:
            if bank.delete_client(name):
                messagebox.showinfo("Success", f"Client '{name}' deleted.")
            else:
                messagebox.showerror("Error", f"Client '{name}' not found.")

    # --- Admin Dashboard ---
    def create_admin_frame(self):
        self.active_frame = tk.Frame(self)
        self.active_frame.pack(pady=10)
        tk.Label(self.active_frame, text="Admin Dashboard", font=("Arial", 14)).pack(pady=5)

        self.client_listbox = tk.Listbox(self.active_frame, width=60)
        self.client_listbox.pack(pady=5)
        tk.Button(self.active_frame, text="Refresh Client List", command=self.refresh_client_list, width=20).pack(
            pady=5)
        tk.Button(self.active_frame, text="Back", command=self.logout, width=20).pack(pady=5)
        self.refresh_client_list()

    def refresh_client_list(self):
        self.client_listbox.delete(0, tk.END)
        for name, client in bank.clients.items():
            accounts_info = ", ".join(f"{acc}: ${bal}" for acc, bal in client.accounts.items())
            info = f"{name} - Accounts: {accounts_info if accounts_info else 'None'}"
            self.client_listbox.insert(tk.END, info)


if __name__ == "__main__":
    app = BankingGUI()
    app.mainloop()