from tkinter import NSEW, SINGLE, Listbox, StringVar, Tk, Frame, Button, Label, Entry, NE
from tkinter import ttk
from modules import passwords as pw, db
import clipboard

root = Tk()
root.title("Passwords")
root.rowconfigure(0,weight=1)
root.columnconfigure(0,weight=1)

PWManager = pw.Manager()
class PWGui:
    def __init__(self, master):
        container=Frame(master)
        container.grid(row=0,column=0,padx=10,pady=10,sticky=NSEW)
        self.frames = {}
        for F in (LoginScreen,SignUpScreen,MainScreen,NewEntryScreen,EditEntryScreen):
            
            frame = F(container, self)
            # the windows class acts as the root window for the frames.
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(LoginScreen)
    def show_frame(self, cont):
        frame = self.frames[cont]
        # raises the current frame to the top
        frame.event_generate("<<ShowFrame>>")
        frame.tkraise()
        
class LoginScreen(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        # Assign the controller to a class variable so we can access it from other Methods
        self.controller = controller
        
        self.title_label = Label(self, text="Login").grid(row=0,column=0)
        
        self.user_label = Label(self, text="Username").grid(row=1,column=0)
        self.user_entry = Entry(self)
        self.user_entry.grid(row=1,column=1,columnspan=2)
        
        self.pass_label = Label(self, text="Password").grid(row=2,column=0)
        self.pass_entry = Entry(self,show="*")
        self.pass_entry.grid(row=2,column=1,columnspan=2)
        self.login_state_var = StringVar()
        self.login_state_label = Label(self, textvariable=self.login_state_var).grid(row=3,column=1)
        
        self.login_button = Button(self,text="Login",command=self.login).grid(row=4,column=1)
        self.signup_button = Button(self,text="Create User",command=lambda: self.controller.show_frame(SignUpScreen)).grid(row=4,column=2)
    
    def login(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()
        self.user_entry.delete(0,"end")
        self.pass_entry.delete(0,"end")
        try:
            PWManager.login(username,password)
            self.controller.show_frame(MainScreen)
        except (pw.AuthenticationError,db.UserDoesNotExist):
            self.login_state_var.set("Login Failed")
            
            
class SignUpScreen(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        # Assign the controller to a class variable so we can access it from other Methods
        self.controller = controller
        
        self.title_label = Label(self, text="Create User").grid(row=0,column=0)
        
        self.user_label = Label(self, text="Username").grid(row=1,column=0)
        self.user_entry = Entry(self)
        self.user_entry.grid(row=1,column=1,columnspan=2)
        
        self.pass_label = Label(self, text="Password").grid(row=2,column=0)
        self.pass_entry = Entry(self,show="*")
        self.pass_entry.grid(row=2,column=1,columnspan=2)
        
        self.pass_confirm_label = Label(self, text="Confirm Password").grid(row=3,column=0)
        self.pass_confirm_entry = Entry(self,show="*")
        self.pass_confirm_entry.grid(row=3,column=1,columnspan=2)
        
        self.signup_state_var = StringVar()
        self.signup_state_label = Label(self, textvariable=self.signup_state_var).grid(row=4,column=0,columnspan=4)
        
        self.signup_button = Button(self,text="Create User",command=self.sign_up).grid(row=5,column=1)
        self.login_button = Button(self,text="Login",command=lambda: controller.show_frame(LoginScreen)).grid(row=5,column=2)
        
    def sign_up(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()
        confirm = self.pass_confirm_entry.get()
        self.user_entry.delete(0,"end")
        self.pass_entry.delete(0,"end")
        self.pass_confirm_entry.delete(0,"end")
        try:
            PWManager.create_user(username,password,confirm)
            self.signup_state_var.set(f"{username} has been created. You can now login")
        except (db.UserAlreadyExists,pw.ValidationError) as e:
            self.signup_state_var.set(str(e))
        
class MainScreen(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        # Assign the controller to a class variable so we can access it from other Methods
        self.controller = controller
        self.bind("<<ShowFrame>>", self.on_show_frame)
        self.title_label = Label(self, text="All Passwords").grid(row=0,column=0)
        
        self.user_var = StringVar()
        self.user_var.set(PWManager.user_name)
        self.user_label = Label(self, textvariable=self.user_var,anchor="w").grid(row=0,column=1)
        #self.entries_list = Listbox(self,width=40, height=15, selectmode=SINGLE).grid(row=1,column=0,rowspan=5)
        
        self.main_state_var = StringVar()
        self.signup_state_label = Label(self, textvariable=self.main_state_var).grid(row=6,column=0,columnspan=4)
        
        self.new_entry_button = Button(self,text="Create New Entry",command=lambda: controller.show_frame(NewEntryScreen)).grid(row=1,column=1,padx=10)
        self.new_entry_button = Button(self,text="Edit Entry",command=self.edit_entry).grid(row=2,column=1,padx=10)
        self.new_entry_button = Button(self,text="Copy Site",command=self.copy_site).grid(row=3,column=1,padx=10)
        self.new_entry_button = Button(self,text="Copy Username",command=self.copy_username).grid(row=4,column=1,padx=10)
        self.new_entry_button = Button(self,text="Copy Password",command=self.copy_password).grid(row=5,column=1,padx=10)
        self.new_entry_button = Button(self,text="Logout",command=self.logout).grid(row=6,column=1,padx=10)
    def on_show_frame(self, event):
        self.user_var.set(f"Logged in User: {PWManager.user_name}")
        
        self.entries_list = Listbox(self,width=40, height=15, selectmode=SINGLE)
        entries = PWManager.get_all_entries()
        self.entries_dict = {}
        count = 0
        for element in entries:
            self.entries_dict[count] = element[0]
            count+=1
            self.entries_list.insert(element[0],f"{element[1]} ({element[2]})")
        self.entries_list.grid(row=1,column=0,rowspan=5)

    def copy_password(self):
        try:
            id = self.entries_dict[self.entries_list.curselection()[0]]
            clipboard.copy(PWManager.get_password(id))
            self.main_state_var.set("Password copied")
        except:
            self.main_state_var.set("Error copying password")
            
    def copy_username(self):
        try:
            id = self.entries_dict[self.entries_list.curselection()[0]]
            clipboard.copy(PWManager.get_username(id))
            self.main_state_var.set("Username copied")
        except:
            self.main_state_var.set("Error copying username")
            
    def copy_site(self):
        try:
            id = self.entries_dict[self.entries_list.curselection()[0]]
            clipboard.copy(PWManager.get_site(id))
            self.main_state_var.set("Site copied")
        except:
            self.main_state_var.set("Error copying site")

    def edit_entry(self):
        try:
            self.active_id = self.entries_dict[self.entries_list.curselection()[0]]
            self.controller.show_frame(EditEntryScreen)
        except IndexError:
            self.main_state_var.set("No entry has been selected")
        
    def logout(self):
        self.entries_list.delete(0)
        PWManager.logout()
        self.controller.show_frame(LoginScreen)
        
class EditEntryScreen(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        # Assign the controller to a class variable so we can access it from other Methods
        self.controller = controller
        self.bind("<<ShowFrame>>", self.on_show_frame)
        self.title_label = Label(self, text="Create new entry").grid(row=0,column=0)
        
        self.site_label = Label(self, text="Website").grid(row=1,column=0)
        self.site_entry = Entry(self)
        self.site_entry.grid(row=1,column=1,columnspan=2)
        
        self.user_label = Label(self, text="Username").grid(row=2,column=0)
        self.user_entry = Entry(self)
        self.user_entry.grid(row=2,column=1,columnspan=2)
        
        self.pass_label = Label(self, text="Password").grid(row=3,column=0)
        self.pass_entry = Entry(self)
        self.pass_entry.grid(row=3,column=1,columnspan=2)
        
        self.edit_var = StringVar()
        self.edit_label = Label(self,textvariable=self.edit_var).grid(row=4,column=1)
        
        self.main_screen_button = Button(self,text="Back",command=lambda: controller.show_frame(MainScreen)).grid(row=5,column=0)
        self.create_entry_button = Button(self,text="Update Entry",command=self.edit_entry).grid(row=5,column=1)
        self.generate_password_button = Button(self,text="Generate Password",command=self.generate_password).grid(row=5,column=2)
        self.reset_password_button = Button(self,text="Reset",command=self.reset_password).grid(row=5,column=3)
    
    def on_show_frame(self, event):
        self.id = self.controller.frames[MainScreen].active_id
        self.controller.frames[MainScreen].active_id = None
        self.entry = PWManager.get_single_entry_id(self.id)
        self.user_entry.delete(0,"end")
        self.site_entry.delete(0,"end")
        self.pass_entry.delete(0,"end")
        self.site_entry.insert(0,self.entry[0])
        self.user_entry.insert(0,self.entry[1])
        self.pass_entry.insert(0,self.entry[2])
        self.pass_entry["state"] = "readonly"
    
    def edit_entry(self):
        site = self.site_entry.get()
        user = self.user_entry.get()
        pwd= self.pass_entry.get()
        if site == self.entry[0] and user == self.entry[1] and pwd == self.entry[2]:
            self.edit_var.set("Nothing changed")
        else:
            try:
                PWManager.edit_entry(self.id,site,user,pwd)
                self.edit_var.set("Entry Edited")
            except pw.NotLoggedInError:
                self.controller.show_frame(MainScreen)
            except db.EntryAlreadyExists as e:
                self.edit_var.set(str(e))
    
    def generate_password(self):
        self.pass_entry = Entry(self)
        self.pass_entry.grid(row=3,column=1,columnspan=2)
        self.pass_entry.insert(0,PWManager.generate_password())
        self.pass_entry['state'] = 'readonly'
        self.edit_var.set("Password generated")
        
    def reset_password(self):
        self.pass_entry = Entry(self,show="*")
        self.pass_entry.grid(row=3,column=1,columnspan=2)
        
class NewEntryScreen(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)

        # Assign the controller to a class variable so we can access it from other Methods
        self.controller = controller

        self.title_label = Label(self, text="Create new entry").grid(row=0,column=0)
        
        self.site_label = Label(self, text="Website").grid(row=1,column=0)
        self.site_entry = Entry(self)
        self.site_entry.grid(row=1,column=1,columnspan=2)
        
        self.user_label = Label(self, text="Username").grid(row=2,column=0)
        self.user_entry = Entry(self)
        self.user_entry.grid(row=2,column=1,columnspan=2)
        
        self.pass_label = Label(self, text="Password").grid(row=3,column=0)
        self.pass_entry = Entry(self,show="*")
        self.pass_entry.grid(row=3,column=1,columnspan=2)
        
        self.create_var = StringVar()
        self.create_label = Label(self,textvariable=self.create_var).grid(row=4,column=1)
        
        self.main_screen_button = Button(self,text="Back",command=lambda: controller.show_frame(MainScreen)).grid(row=5,column=0)
        self.create_entry_button = Button(self,text="Create Entry",command=self.create_entry).grid(row=5,column=1)
        self.generate_password_button = Button(self,text="Generate Password",command=self.generate_password).grid(row=5,column=2)
        self.reset_password_button = Button(self,text="Reset",command=self.reset_password).grid(row=5,column=3)
        
    def create_entry(self):
        site = self.site_entry.get()
        user = self.user_entry.get()
        pwd= self.pass_entry.get()
        try:
            PWManager.create_entry(site,user,pwd)
            self.pass_entry["state"] = "normal"
            self.user_entry.delete(0,"end")
            self.site_entry.delete(0,"end")
            self.pass_entry.delete(0,"end")
            self.create_var.set("Entry created")
        except pw.NotLoggedInError:
            self.controller.show_frame(MainScreen)
        except db.EntryAlreadyExists as e:
            self.create_var.set(str(e))
            
        
    def generate_password(self):
        self.pass_entry = Entry(self)
        self.pass_entry.grid(row=3,column=1,columnspan=2)
        self.pass_entry.insert(0,PWManager.generate_password())
        self.pass_entry['state'] = 'readonly'
        self.create_var.set("Password generated")
        
    def reset_password(self):
        self.pass_entry = Entry(self,show="*")
        self.pass_entry.grid(row=3,column=1,columnspan=2)
        
        
MainApp = PWGui(root)
root.mainloop()