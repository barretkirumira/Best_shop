import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import mysql.connector
from mysql.connector import Error

class DbConfig:
    def __init__(self,
                 host="10.233.204.91",
                 port=3306,
                 user="root",
                 password="*Barret1*",
                 database="cleanshopdatabase"):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

# This is a static prototype GUI layout (no database connected)
# It demonstrates the full multi-page design using CustomTkinter.

global lst 
lst = []

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Grocery Price Tracker Prototype")
        self.geometry("1200x750")

        # Navigation bar
        self.navbar = ctk.CTkFrame(self, height=60)
        self.navbar.pack(fill="x")

        self.btn_home = ctk.CTkButton(self.navbar, text="Home", command=self.load_home)
        self.btn_products = ctk.CTkButton(self.navbar, text="Products", command=self.load_products)
        self.btn_add_price = ctk.CTkButton(self.navbar, text="Add Price", command=self.load_add_price)
        self.btn_insights = ctk.CTkButton(self.navbar, text="Insights", command=self.load_insights)

        self.btn_home.pack(side="left", padx=10, pady=10)
        self.btn_products.pack(side="left", padx=10, pady=10)
        self.btn_add_price.pack(side="left", padx=10, pady=10)
        self.btn_insights.pack(side="left", padx=10, pady=10)

        # Main content frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)

        self.load_home()

    def clear_main(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_coming_soon(self, feature_name):
        """Display a coming soon popup"""
        popup = ctk.CTkToplevel(self)
        popup.title("Coming Soon")
        popup.geometry("400x200")
        popup.resizable(False, False)

        ctk.CTkLabel(popup, text="🚀 Coming Soon", font=("Arial", 24, "bold")).pack(pady=20)
        ctk.CTkLabel(popup, text=f"{feature_name} is under development.", font=("Arial", 14)).pack(pady=10)
        ctk.CTkLabel(popup, text="Stay tuned for updates!", font=("Arial", 12)).pack(pady=10)

        ctk.CTkButton(popup, text="OK", command=popup.destroy).pack(pady=20)

    # HOME SCREEN
    def load_home(self):
        global lst
        self.clear_main()
        title = ctk.CTkLabel(self.main_frame, text="Welcome", font=("Arial", 32))
        title.pack(pady=20)

        search_frame = ctk.CTkFrame(self.main_frame)
        search_frame.pack(pady=10)
        ctk.CTkLabel(search_frame, text="Search Product:").pack(side="left", padx=10)
        ctk.CTkEntry(search_frame, width=300, placeholder_text="Type to search...").pack(side="left")

        pop_label = ctk.CTkLabel(self.main_frame, text="Popular Items", font=("Arial", 24))
        pop_label.pack(pady=20)

        pop_container = ctk.CTkFrame(self.main_frame)
        pop_container.pack(pady=10)

        for item in ["Milk", "Bread", "Chicken"]:
            ctk.CTkButton(pop_container, text=item, width=150, command=lambda i=item: self.show_coming_soon(f"{i} Details")).pack(side="left", padx=15, pady=10)

        recent = ctk.CTkLabel(self.main_frame, text="Testing outputting from database", font=("Arial", 24))
        recent.pack(pady=20)

        table_frame = ctk.CTkFrame(self.main_frame)
        table_frame.pack(pady=10)

        columns = ("top-level", "attribute", "disaggregate", "value")
        table = ttk.Treeview(table_frame, columns=columns, show="headings", height=7)
        for col in columns:
            table.heading(col, text=col.capitalize())
            table.column(col, width=150)

        table.pack()

        # Populate table from database results
        for r in lst:
            table.insert("", tk.END, values=(r.get("top-level"), r.get("attribute"), r.get("disaggregate"), r.get("value")))

    # PRODUCTS SCREEN
    def load_products(self):
        self.clear_main()
        title = ctk.CTkLabel(self.main_frame, text="Products", font=("Arial", 32))
        title.pack(pady=20)

        filter_frame = ctk.CTkFrame(self.main_frame)
        filter_frame.pack(pady=10)

        ctk.CTkLabel(filter_frame, text="Category:").pack(side="left", padx=5)
        ctk.CTkComboBox(filter_frame, values=["Dairy", "Grain", "Meat"]).pack(side="left", padx=5)

        ctk.CTkLabel(filter_frame, text="Brand:").pack(side="left", padx=5)
        ctk.CTkComboBox(filter_frame, values=["Generic", "Brand A", "Brand B"]).pack(side="left", padx=5)

        ctk.CTkButton(filter_frame, text="Reset Filters", command=lambda: self.show_coming_soon("Filter Reset")).pack(side="left", padx=10)

        # Product list
        list_frame = ctk.CTkScrollableFrame(self.main_frame, width=1000, height=500)
        list_frame.pack(pady=20)

        for prod in ["Milk", "Bread", "Rice", "Apples", "Chicken", "Beef"]:
            row = ctk.CTkFrame(list_frame)
            row.pack(fill="x", pady=5)
            ctk.CTkButton(row, text=prod, font=("Arial", 20), width=100, command=lambda p=prod: self.show_coming_soon(f"{p} Details")).pack(side="left", padx=20)
            ctk.CTkLabel(row, text="Category: Demo").pack(side="left", padx=20)
            ctk.CTkLabel(row, text="Trend: →").pack(side="left", padx=20)

    # ADD PRICE SCREEN
    def load_add_price(self):
        self.clear_main()
        title = ctk.CTkLabel(self.main_frame, text="Add New Price", font=("Arial", 32))
        title.pack(pady=20)

        form = ctk.CTkFrame(self.main_frame)
        form.pack(pady=20)

        fields = ["top-level", "attribute", "disaggregate", "value"]
        self.entries = {}
        for f in fields:
            row = ctk.CTkFrame(form)
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=f + ":", width=120).pack(side="left")
            entry = ctk.CTkEntry(row, width=300)
            entry.pack(side="left", padx=10)
            self.entries[f] = entry

        ctk.CTkButton(self.main_frame, text="Submit", width=200, command=lambda: self.show_coming_soon("Price Submission")).pack(pady=20)

    # INSIGHTS SCREEN
    def load_insights(self):
        self.clear_main()
        title = ctk.CTkLabel(self.main_frame, text="Insights & Predictions", font=("Arial", 32))
        title.pack(pady=20)

        pick = ctk.CTkComboBox(self.main_frame, values=["Milk", "Bread", "Chicken"], width=200)
        pick.pack(pady=10)

        chart_placeholder = ctk.CTkFrame(self.main_frame, width=900, height=300)
        chart_placeholder.pack(pady=20)
        ctk.CTkLabel(chart_placeholder, text="[chart placeholder] \n Coming Soon", font=("Arial", 18)).place(relx=0.5, rely=0.5, anchor="center")

        rec = ctk.CTkFrame(self.main_frame)
        rec.pack(pady=20)

        ctk.CTkLabel(rec, text="Recommended Month: July", font=("Arial", 20)).pack(pady=5)
        ctk.CTkLabel(rec, text="Confidence: 82%", font=("Arial", 20)).pack(pady=5)
        ctk.CTkLabel(rec, text="Prices expected to drop next month.").pack(pady=5)


if __name__ == "__main__":
    cfg = DbConfig()
    conn = mysql.connector.connect(
            host=cfg.host,
            port=cfg.port,
            user=cfg.user,
            password=cfg.password,
            ssl_disabled=True,
            database=cfg.database
            )
    sql = "Select `top-level`, attribute, disaggregate, value FROM cpiforecast WHERE disaggregate Not Like %s LIMIT 5;"
    #sql = "show databases;"
    params = ('',)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, params)
    for row in cursor:
        lst.append(row)
    cursor.close()
    conn.close()
    app = App()
    app.mainloop()
