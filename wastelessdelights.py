import tkinter as tk
from tkinter import ttk
import mysql.connector
from PIL import Image, ImageTk
import ctypes
from PyQt5 import QtGui
import sys

def show_instructions():
    selected_item = recipe_treeview.selection()
    if selected_item:
        selected_recipe = recipe_treeview.item(selected_item)['text']
        try:
            connection = mysql.connector.connect(
                host="10.158.32.148",
                port=3307,
                user="liam",
                password="Dollareins$1",
                database="recipes"
            )
            cursor = connection.cursor()
            cursor.execute("SELECT ingredients, instructions FROM recipe WHERE name = %s", (selected_recipe,))
            recipe_info = cursor.fetchone()
            if recipe_info:
                ingredients, instructions = recipe_info
                instructions_text.config(state="normal")
                instructions_text.delete("1.0", tk.END)
                instructions_text.insert(tk.END, f"Zutaten:{ingredients}\n\nAnleitung:{instructions}")
                instructions_text.config(state="disabled")
                instructions_text.place(relx=0.02, rely=0.87, relwidth=0.96, relheight=0.1)
            else:
                instructions_text.config(state="normal")
                instructions_text.delete("1.0", tk.END)
                instructions_text.insert(tk.END, "Rezept nicht gefunden.")
                instructions_text.config(state="disabled")
                instructions_text.place_forget()
            connection.close()
        except mysql.connector.Error as err:
            print("Error fetching instructions:", err)
    else:
        instructions_text.config(state="normal")
        instructions_text.delete("1.0", tk.END)
        instructions_text.insert(tk.END, "Bitte wählen Sie ein Rezept aus.")
        instructions_text.config(state="disabled")
        instructions_text.place_forget()
   
def populate_treeview(matching_recipes=None):
    recipe_treeview.delete(*recipe_treeview.get_children())
    if matching_recipes is None:
        try:
            connection = mysql.connector.connect(
                host="10.158.32.148",
                port=3307,
                user="liam",
                password="Dollareins$1",
                database="recipes"
            )
            cursor = connection.cursor()
            cursor.execute("SELECT name FROM recipe")
            matching_recipes = cursor.fetchall()
            connection.close()
        except mysql.connector.Error as err:
            print("Error fetching recipes:", err)
    if matching_recipes:
        for recipe in matching_recipes:
            recipe_name = recipe[0]
            item = recipe_treeview.insert("", "end", text=recipe_name)  
        recipe_treeview.column("#0", width=200)
        recipe_treeview_frame.place(relx=0.02, rely=0.15, relwidth=0.96, relheight=0.7)
    else:
        instructions_text.config(state="normal")
        instructions_text.delete("1.0", tk.END)
        instructions_text.insert(tk.END, "Keine Rezepte gefunden!")
        instructions_text.config(state="disabled")
        instructions_text.place_forget()

def search_recipe():
    search_input = search_entry.get().strip()
    if search_input:
        try:
            connection = mysql.connector.connect(
                host="10.158.32.148",
                port=3307,
                user="liam",
                password="Dollareins$1",
                database="recipes"
            )
            cursor = connection.cursor()
            search_terms = []
            if "&" in search_input:
                search_terms = search_input.split("&")
                query = "SELECT name FROM recipe WHERE"
                for term in search_terms:
                    query += " ingredients LIKE '%" + term.strip() + "%' AND"
                query = query[:-4]
            elif "," in search_input:
                search_terms = search_input.split(",")
                query = "SELECT DISTINCT name FROM recipe WHERE"
                for term in search_terms:
                    query += " ingredients LIKE '%" + term.strip() + "%' OR"
                query = query[:-3]
            else:
                query = "SELECT DISTINCT name FROM recipe WHERE ingredients LIKE '%" + search_input.strip() + "%'"
            cursor.execute(query)
            matching_recipes = cursor.fetchall()
            recipe_treeview.delete(*recipe_treeview.get_children())
            if matching_recipes:
                for recipe in matching_recipes:
                    recipe_treeview.insert("", "end", text=recipe[0])  # Name des Rezepts einfügen
                recipe_treeview.column("#0", width=200)
                recipe_treeview_frame.place(relx=0.02, rely=0.15, relwidth=0.96, relheight=0.7)
            else:
                error_label.config(text="Die Zutat konnte keinem Rezept zugeordnet werden!")
                error_label.place(relx=0.02, rely=0.17, relwidth=0.96, relheight=0.05)
            connection.close()
        except mysql.connector.Error as err:
            print("Error searching for recipe:", err)
    else:
        error_label.config(text="Bitte geben Sie etwas ins Suchfeld ein!", foreground="red")
        error_label.place(relx=0.02, rely=0.17, relwidth=0.96, relheight=0.05)

def clear_error():
    error_label.config(text="")

def create_recipe():
    main_frame.place_forget()
    create_recipe_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

def save_recipe():
    global edit_mode
    recipe_name = recipe_name_entry.get()
    recipe_content = recipe_content_entry.get()
    recipe_prep = recipe_prep_entry.get()
    if recipe_name and recipe_content and recipe_prep:
        try:
            connection = mysql.connector.connect(
                host="10.158.32.148",
                port=3307,
                user="liam",
                password="Dollareins$1",
                database="recipes"
            )
            cursor = connection.cursor()
            if edit_mode:
                selected_item = recipe_treeview.selection()
                if selected_item:
                    selected_recipe = recipe_treeview.item(selected_item)['text']
                    cursor.execute("UPDATE recipe SET name = %s, ingredients = %s, instructions = %s WHERE name = %s", (recipe_name, recipe_content, recipe_prep, selected_recipe))
                    print("Rezept erfolgreich aktualisiert!")
            else:
                cursor.execute("INSERT INTO recipe (name, ingredients, instructions) VALUES (%s, %s, %s)", (recipe_name, recipe_content, recipe_prep))
                print("Rezept erfolgreich gespeichert!")
            connection.commit()
            connection.close()
            cancel_recipe()
        except mysql.connector.Error as err:
            print("Error saving recipe:", err)
    else:
        print("Bitte geben Sie sowohl den Rezeptnamen, den Rezeptinhalt als auch die Rezeptzubereitung ein!")

def cancel_recipe():
    recipe_name_entry.delete(0, tk.END)
    recipe_content_entry.delete(0, tk.END)
    recipe_prep_entry.delete(0, tk.END)
    create_recipe_frame.place_forget()
    main_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
    global edit_mode
    edit_mode = False

def edit_recipe():
    global edit_mode
    edit_mode = True
    selected_item = recipe_treeview.selection()
    if selected_item:
        selected_recipe = recipe_treeview.item(selected_item)['text']
        # Verberge den "Show-More" Bereich
        instructions_text.place_forget()
        try:
            connection = mysql.connector.connect(
                host="10.158.32.148",
                port=3307,
                user="liam",
                password="Dollareins$1",
                database="recipes"
            )
            cursor = connection.cursor()
            cursor.execute("SELECT name, ingredients, instructions FROM recipe WHERE name = %s", (selected_recipe,))
            recipe_info = cursor.fetchone()
            if recipe_info:
                recipe_name, recipe_ingredients, recipe_instructions = recipe_info
                recipe_name_entry.delete(0, tk.END)
                recipe_name_entry.insert(0, recipe_name)
                recipe_content_entry.delete(0, tk.END)
                recipe_content_entry.insert(0, recipe_ingredients)
                recipe_prep_entry.delete(0, tk.END)
                recipe_prep_entry.insert(0, recipe_instructions)
                main_frame.place_forget()
                create_recipe_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            else:
                print("Rezept nicht gefunden.")
            connection.close()
        except mysql.connector.Error as err:
            print("Error fetching recipe:", err)
    else:
        print("Bitte wählen Sie ein Rezept aus, um es zu bearbeiten.")

def delete_recipe(recipe_name):
    try:
        connection = mysql.connector.connect(
            host="10.158.32.148",
            port=3307,
            user="liam",
            password="Dollareins$1",
            database="recipes"
        )
        cursor = connection.cursor()
        cursor.execute("DELETE FROM recipe WHERE name = %s", (recipe_name,))
        connection.commit()
        connection.close()
        print("Rezept erfolgreich gelöscht!")
        # Verberge den "Show-More" Bereich nach dem Löschen
        instructions_text.place_forget()
        search_recipe()
    except mysql.connector.Error as err:
        print("Error deleting recipe:", err)

root = tk.Tk()
myappid = 'mycompany.myproduct.subproduct.version'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

root.title("Recipe Search")
ico = Image.open('icon_py.ico')
photo = ImageTk.PhotoImage(ico)
root.wm_iconphoto(False, photo)
root.minsize(600, 400)

style = ttk.Style()
style.theme_use("clam")
style.configure(".", background="white")
style.configure("TButton", foreground="white", background="#4caf50", font=("Arial", 18))

image = Image.open('icon_py.ico')
image = ImageTk.PhotoImage(image)
image_label = tk.Label(root, image=image)
image_label.pack()

main_frame = ttk.Frame(root)
main_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
welcome_label = ttk.Label(root, text="Willkommen zu Wasteless Delights", font=("Arial", 20, "bold"))
welcome_label.place(relx=0.5, rely=0.02, relwidth=1, relheight=0.05, anchor="n")

search_label = ttk.Label(main_frame, text="Search Recipe:")
search_label.place(relx=0.02, rely=0.08, relwidth=0.15, relheight=0.08)

search_entry = ttk.Entry(main_frame, font=("Arial", 16))
search_entry.place(relx=0.02, rely=0.08, relwidth=0.6, relheight=0.08)

search_button = ttk.Button(main_frame, text="Search", command=search_recipe)
search_button.place(relx=0.65, rely=0.08, relwidth=0.15, relheight=0.08)

create_button = ttk.Button(main_frame, text="Create Recipe", command=create_recipe)
create_button.place(relx=0.82, rely=0.08, relwidth=0.15, relheight=0.08)

create_recipe_frame = ttk.Frame(root)
create_recipe_frame.configure()

recipe_name_label = ttk.Label(create_recipe_frame, text="Rezeptname:")
recipe_name_label.grid(row=0, column=0, padx=10, pady=10)

recipe_name_entry = ttk.Entry(create_recipe_frame, font=("Arial", 16))
recipe_name_entry.grid(row=0, column=1, padx=10, pady=10)

recipe_content_label = ttk.Label(create_recipe_frame, text="Rezeptinhalt:")
recipe_content_label.grid(row=1, column=0, padx=10, pady=10)

recipe_content_entry = ttk.Entry(create_recipe_frame, font=("Arial", 16))
recipe_content_entry.grid(row=1, column=1, padx=10, pady=10)

recipe_prep_label = ttk.Label(create_recipe_frame, text="Rezeptzubereitung:")
recipe_prep_label.grid(row=2, column=0, padx=10, pady=10)

recipe_prep_entry = ttk.Entry(create_recipe_frame, font=("Arial", 16))
recipe_prep_entry.grid(row=2, column=1, padx=10, pady=10)

save_button = ttk.Button(create_recipe_frame, text="Save", command=save_recipe)
save_button.grid(row=3, column=0, padx=10, pady=10)

cancel_button = ttk.Button(create_recipe_frame, text="Cancel", command=cancel_recipe)
cancel_button.grid(row=3, column=1, padx=10, pady=10)

error_label = ttk.Label(main_frame, text="", foreground="red")
error_label.place(relx=0.02, rely=0.92, relwidth=0.96, relheight=0.05)

recipe_treeview_frame = ttk.Frame(main_frame)

recipe_treeview = ttk.Treeview(recipe_treeview_frame, 
columns=("Button", "Button1", "Button2"), selectmode="browse", height=15)
recipe_treeview.heading("#0", text="Recipe Name")

recipe_treeview.heading("Button", text="Show-More")
recipe_treeview.heading("Button1", text="Edit")
recipe_treeview.heading("Button2", text="Delete")

recipe_treeview.pack(side="left", fill="both", expand=True)

def on_button_click(event):
    item_id = recipe_treeview.identify_column(event.x)
    if item_id in ["#1", "#2", "#3"]:  # Überprüfen, ob ein Button im Header angeklickt wurde
        item_values = recipe_treeview.heading(item_id)['text']
        if item_values == "Show-More":
            show_instructions()
        elif item_values == "Edit":
            edit_recipe()
        elif item_values == "Delete":
            selected_item = recipe_treeview.selection()
            if selected_item:
                item_text = recipe_treeview.item(selected_item, 'text')
                delete_recipe(item_text)
    else:
        selected_item = recipe_treeview.focus()
        item_values = recipe_treeview.item(selected_item, 'values')
        if "Show-More" in item_values:
            show_instructions()
        elif "Edit" in item_values:
            edit_recipe()
        elif "Delete" in item_values:
            item_text = recipe_treeview.item(selected_item, 'text')
            delete_recipe(item_text)

def bind_button_click():
    recipe_treeview.bind("<Button-1>", on_button_click)

def cancel_recipe():
    recipe_name_entry.delete(0, tk.END)
    recipe_content_entry.delete(0, tk.END)
    recipe_prep_entry.delete(0, tk.END)
    create_recipe_frame.place_forget()
    main_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

bind_button_click()

instructions_text = tk.Text(root, wrap="word", state="disabled", font=("Arial", 12))

root.mainloop()