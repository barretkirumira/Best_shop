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

        conn=db_connect(); 
        cur=conn.cursor(dictionary=True)
        cur.execute("SELECT category_name FROM product_category ")
        sql = cur.fetchall()
        categories = ["All"] 
        for t in sql:
            categories.append(t['category_name'])
        cur.close(); conn.close()

        filter_category=ctk.CTkComboBox(search_frame,values=categories,width=150)
        filter_category.pack(side="left",padx=5)

        results_frame=ctk.CTkScrollableFrame(self.main,width=1000,height=500)
        results_frame.pack(pady=20)

        def refresh():
            for w in results_frame.winfo_children(): w.destroy()
            name=search_entry.get()
            cat=filter_category.get()

            conn=db_connect(); 
            cur=conn.cursor(dictionary=True)

            if name != "":
                sql="SELECT * FROM product WHERE product_name LIKE %s"

                params=[f"%{name}%"]
                if cat!="All": sql+=" AND category=%s"; params.append(cat)
                cur.execute(sql,params)
                sqlproducts = cur.fetchall()
            else: 
                sql="SELECT * FROM product Inner Join product_category on product.category_id = product_category.category_id "
                params=[]
                if cat!="All": sql+="Where category_name = %s"; params.append(cat)
                cur.execute(sql,params)
                sqlproducts = cur.fetchall()
    
            for p in sqlproducts:
                    row=ctk.CTkFrame(results_frame); row.pack(fill="x",pady=5)
                    ctk.CTkLabel(row,text=f"Product: {p['product_name']:<25}",font=("Arial",20)).pack(side="left",padx=15)
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
            cur.execute("Select * From product where product_name = %s", (entries['Name'].get(),))
            pid = cur.fetchall()
            cur.execute("Select category_id From product_category where category_name = %s", (entries['Category'].get(),))
            cid = cur.fetchall()
            cur.execute("Select brand_id From product_brand where brand_name = %s", (entries['Brand'].get(),))
            bid = cur.fetchall()
            
            if not pid :
                if not cid :
                    cur.execute("INSERT INTO product_category(category_name) VALUES(%s)", (entries['Category'].get(),))
                    cur.execute("Select category_id From product_category where category_name = %s", (entries['Category'].get(),))
                    cid = cur.fetchall()
                if not bid :
                    cur.execute("INSERT INTO product_brand(brand_name) VALUES(%s)", (entries['Brand'].get(),))
                    cur.execute("Select brand_id From product_brand where brand_name = %s", (entries['Brand'].get(),))
                    bid = cur.fetchall()

                cur.execute("INSERT INTO product(product_name,brand_id,category_id) VALUES(%s,%s,%s)",
                        (entries["Name"].get(),bid[0][0],cid[0][0]))
                conn.commit(); cur.close(); conn.close()
                messagebox.showinfo("Success","Product added!")
            else : messagebox.showinfo("Success","Product exists!")

        ctk.CTkButton(self.main,text="Save",width=180,command=submit).pack(pady=15)

#======================== ADD PRICE ========================#
    def load_add_price(self):
        self.clear()
        ctk.CTkLabel(self.main,text="Add Price Entry",font=("Segoe UI Emoji",30)).pack(pady=20)

        conn=db_connect(); cur=conn.cursor(dictionary=True)
        cur.execute("SELECT product_id, product_name FROM product")
        products=[f"{p['product_id']} - {p['product_name']}" for p in cur.fetchall()]
        cur.close(); conn.close()

        dropdown=ctk.CTkComboBox(self.main,values=products,width=280)
        dropdown.pack(pady=15)

        form=ctk.CTkFrame(self.main); form.pack(pady=10)
        row=ctk.CTkFrame(form); row.pack(fill="x",pady=5)
        ctk.CTkLabel(row,text="Location:",width=120).pack(side="left")
        location_entry=ctk.CTkEntry(row,width=280,placeholder_text="Enter location...")
        location_entry.pack(pady=10, side="left")
        row1=ctk.CTkFrame(form); row1.pack(fill="x",pady=5)
        ctk.CTkLabel(row1,text="Store:",width=120).pack(side="left")
        store_entry=ctk.CTkEntry(row1,width=280,placeholder_text="Enter store...")
        store_entry.pack(pady=10, side="left")
        row2=ctk.CTkFrame(form); row2.pack(fill="x",pady=5)
        ctk.CTkLabel(row2,text="Price:",width=120).pack(side="left")
        price_entry=ctk.CTkEntry(row2,width=280,placeholder_text="Enter price...")
        price_entry.pack(pady=10, side="left")

        def save_price():
            pid=dropdown.get().split(" - ")[0]
            conn=db_connect(); cur=conn.cursor()
            #cur.execute("INSERT INTO price_observation(product_id,price) VALUES(%s,%s)",(pid,price_entry.get()))
            cur.execute("Select store_id From store where store_name = %s and location = %s", (store_entry.get(), location_entry.get(),))
            sid = cur.fetchall()
                        
            if not sid :
                cur.execute("INSERT INTO store(store_name, location) VALUES(%s,%s)", (store_entry.get(), location_entry.get(),))
                cur.execute("Select store_id From store where store_name = %s and location = %s", (store_entry.get(), location_entry.get(),))
                sid = cur.fetchall()
               
            cur.execute("INSERT INTO price_observation(product_id, store_id, observed_price, observation_date) VALUES(%s,%s,%s,now())",
                        (pid,sid[0][0],price_entry.get(),))
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
        cur.execute("SELECT avg_price, date FROM bg_price_history WHERE product_id=%s ORDER BY date DESC",(product_id,))
        for r in cur.fetchall(): table.insert("",tk.END,values=(r["avg_price"],r["date"]))
        cur.execute("SELECT observed_price, observation_date FROM price_observation WHERE product_id=%s ORDER BY observation_date DESC",(product_id,))
        for r in cur.fetchall(): table.insert("",tk.END,values=(r["observed_price"],r["observation_date"]))
        cur.close(); conn.close()

#======================== RUN ========================#
if __name__=="__main__":
    app=App()
    app.mainloop()
