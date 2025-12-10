import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

#======================== DB CONFIG ========================#
class DbConfig:
    def __init__(self,
                 host="10.233.204.91",   # Already connected server ✔
                 port=3306,
                 user="root",
                 password="*Barret1*",         # <- your password here
                 database="cleanshopdatabase"):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

def db_connect():
    cfg = DbConfig()
    return mysql.connector.connect(
        host=cfg.host,
        user=cfg.user,
        password=cfg.password,
        database=cfg.database
    )

#======================== APP GUI ========================#
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Grocery Price Tracker")
        self.geometry("1200x750")

        # Navbar
        nav = ctk.CTkFrame(self, height=60)
        nav.pack(fill="x")
        ctk.CTkButton(nav,text="Home",command=self.load_home).pack(side="left",padx=15,pady=10)
        ctk.CTkButton(nav,text="Products",command=self.load_products).pack(side="left",padx=15)
        ctk.CTkButton(nav,text="Add Product",command=self.load_add_product).pack(side="left",padx=15)
        ctk.CTkButton(nav,text="Add Price",command=self.load_add_price).pack(side="left",padx=15)

        # Main Container
        self.main = ctk.CTkFrame(self,corner_radius=0)
        self.main.pack(fill="both",expand=True)

        self.load_home()

    def clear(self): 
        for w in self.main.winfo_children(): w.destroy()

#======================== HOME ========================#
    def load_home(self):
        self.clear()
        ctk.CTkLabel(self.main,text="CPI Forecast View",font=("Segoe UI Emoji",32)).pack(pady=20)

        table_frame=ctk.CTkFrame(self.main); table_frame.pack(pady=10)
        columns=("top","attribute","unit","value")
        table=ttk.Treeview(table_frame,columns=columns,show="headings",height=14)
        for c in columns: table.heading(c,text=c.upper()); table.column(c,width=200)
        table.pack()

        conn=db_connect()
        cur=conn.cursor(dictionary=True)
        cur.execute("SELECT `Top-level`,`Attribute`,`Unit`,`Value` FROM cpiforecast LIMIT 50")
        for r in cur.fetchall(): table.insert("",tk.END,values=(r["Top-level"],r["Attribute"],r["Unit"],r["Value"]))
        cur.close(); conn.close()

#======================== PRODUCT LIST + SEARCH ========================#
    def load_products(self):
        self.clear()
        ctk.CTkLabel(self.main,text="Products",font=("Segoe UI Emoji",32)).pack(pady=20)

        search_frame=ctk.CTkFrame(self.main); search_frame.pack(pady=10)
        search_entry=ctk.CTkEntry(search_frame,width=280,placeholder_text="Search name...")
        search_entry.pack(side="left",padx=5)

        filter_category=ctk.CTkComboBox(search_frame,values=["All","Dairy","Meat","Fruit","Grain","Other"],width=150)
        filter_category.pack(side="left",padx=5)

        results_frame=ctk.CTkScrollableFrame(self.main,width=1000,height=500)
        results_frame.pack(pady=20)

        def refresh():
            for w in results_frame.winfo_children(): w.destroy()
            name=search_entry.get()
            cat=filter_category.get()

            conn=db_connect(); 
            cur=conn.cursor(dictionary=True)

            #sqlproducts = []
            if name != "":
                sql="SELECT * FROM product WHERE product_name LIKE %s"

                params=[f"%{name}%"]
                if cat!="All": sql+=" AND category=%s"; params.append(cat)
                cur.execute(sql,params)
                sqlproducts = cur.fetchall()
            else: 
                sql="SELECT * FROM product"
                cur.execute(sql)
                sqlproducts = cur.fetchall()
    
            for p in sqlproducts:
                    row=ctk.CTkFrame(results_frame); row.pack(fill="x",pady=5)
                    ctk.CTkLabel(row,text=f"Product: {p['product_name']:<20}",font=("Arial",20)).pack(side="left",padx=15)
                    ctk.CTkLabel(row,text=f"Category: {p['category_id']:<5}").pack(side="left",padx=20)
                    ctk.CTkLabel(row,text=f"Brand: {p['brand_id']:<5}").pack(side="left",padx=20)
                    ctk.CTkButton(row,text="History",command=lambda id=p["product_id"]:self.show_price_history(id)).pack(side="right",padx=20)

            cur.close(); conn.close()

        ctk.CTkButton(search_frame,text="Search",command=refresh).pack(side="left",padx=10)
        refresh()

#======================== ADD PRODUCT ========================#
    def load_add_product(self):
        self.clear()
        ctk.CTkLabel(self.main,text="Add New Product",font=("Segoe UI Emoji",30)).pack(pady=20)

        form=ctk.CTkFrame(self.main); form.pack(pady=10)
        fields=["Name","Brand","Category"]
        entries={}
        for f in fields:
            row=ctk.CTkFrame(form); row.pack(fill="x",pady=5)
            ctk.CTkLabel(row,text=f+":",width=120).pack(side="left")
            e=ctk.CTkEntry(row,width=280); e.pack(side="left",padx=10)
            entries[f]=e

        def submit():
            conn=db_connect(); cur=conn.cursor()
            cur.execute("INSERT INTO product(name,brand,category) VALUES(%s,%s,%s)",
                        (entries["Name"].get(),entries["Brand"].get(),entries["Category"].get()))
            conn.commit(); cur.close(); conn.close()
            messagebox.showinfo("Success","Product added!")

        ctk.CTkButton(self.main,text="Save",width=180,command=submit).pack(pady=15)

#======================== ADD PRICE ========================#
    def load_add_price(self):
        self.clear()
        ctk.CTkLabel(self.main,text="Add Price Entry",font=("Segoe UI Emoji",30)).pack(pady=20)

        conn=db_connect(); cur=conn.cursor(dictionary=True)
        cur.execute("SELECT id,name FROM product")
        products=[f"{p['id']} - {p['name']}" for p in cur.fetchall()]
        cur.close(); conn.close()

        dropdown=ctk.CTkComboBox(self.main,values=products,width=280)
        dropdown.pack(pady=15)

        price_entry=ctk.CTkEntry(self.main,width=280,placeholder_text="Enter price...")
        price_entry.pack(pady=10)

        def save_price():
            pid=dropdown.get().split(" - ")[0]
            conn=db_connect(); cur=conn.cursor()
            cur.execute("INSERT INTO price_history(product_id,price) VALUES(%s,%s)",(pid,price_entry.get()))
            conn.commit(); cur.close(); conn.close()
            messagebox.showinfo("Added","Price saved!")

        ctk.CTkButton(self.main,text="Save Price",command=save_price).pack(pady=15)

#======================== SHOW PRICE HISTORY ========================#
    def show_price_history(self,product_id):
        popup=ctk.CTkToplevel(self)
        popup.title("Price History"); popup.geometry("600x500")

        table=ttk.Treeview(popup,columns=("price","date"),show="headings",height=20)
        table.heading("price",text="Price ($)"); table.heading("date",text="Date")
        table.pack(fill="both",expand=True,pady=20)

        conn=db_connect(); cur=conn.cursor(dictionary=True)
        cur.execute("SELECT price,date FROM price_history WHERE product_id=%s ORDER BY date DESC",(product_id,))
        for r in cur.fetchall(): table.insert("",tk.END,values=(r["price"],r["date"]))
        cur.close(); conn.close()

#======================== RUN ========================#
if __name__=="__main__":
    app=App()
    app.mainloop()
