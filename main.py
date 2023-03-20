import tkinter as tk
import socket
import time


root = tk.Tk()
root.geometry("1600x900")
root.configure(background='#000000')       #4AFE16
root.title("Bobby")

'''
In this program we have three objects:
    1)Login             The user will choose client or server, Login will navigate the user to server or client
    2)Server            
    3)Client
'''

class Login:

    def __init__(self, window):

        # we delete all the old pages(frames) and show the Login page
        for frame in window.winfo_children():
            frame.destroy()
        
       self.choose_label = tk.Label(self.login_frame,
                                text="WELCOME TO BOBBY'S SITE! WHAT TYPE OF GUY ARE YOU ON",font=("Verdana"),width=90,height=32,bg=myclr2
                                     )
        self.server_btn = tk.Button(self.login_frame,
                               text="SERVER",font="Verdana",bg=myclr,fg="black",width=90,height=2,
                               command=self.choosen_server
                               )
        self.client_btn = tk.Button(self.login_frame,
                               text="CLIENT",font="Verdana",bg=myclr,fg="black",width=90,height=2,
                               command=self.choosen_client
                               )

        # Appending our contents
        self.choose_label.pack()
        self.server_btn.pack()
        self.client_btn.pack()

        self.login_frame.pack()
        
    # if user chooses server
    def choosen_server(self):
        run_server = Server(root)
        run_server.connect_page()
        run_server.connect_btn.config(bg='#63e53f')

    # if user chooses client
    def choosen_client(self):
        Client(root)




class Server():

    def __init__(self, window):
        # Deleting old pages(frames)
        for frame in window.winfo_children():
            frame.destroy()
        
        # options bar (left bar)
        self.options_frame = tk.Frame(window)

        self.server_client = tk.Button(window,
                                       text='login',
                                       font=('Arial', 25, 'bold'),
                                       bg='#BEF8AE',
                                       padx=97,
                                       pady=10,
                                       command=lambda: self.indicate(self.server_client, self.server_client_page)
                                       )
        self.connect_btn = tk.Button(window,
                                     text='connection',
                                     font=('Arial', 25, 'bold'),
                                     bg='#BEF8AE',
                                     padx=48,
                                     pady=10,
                                     command=lambda: self.indicate(self.connect_btn, self.connect_page)
                                     )
        self.file_transfer = tk.Button(window,
                                       text='file transfer',
                                       font=('Arial', 25, 'bold'),
                                       bg='#BEF8AE',
                                       padx=45,
                                       pady=10,
                                       command=lambda: self.indicate(self.file_transfer, self.file_transfer_page)
                                       )
        self.setting_btn = tk.Button(window,
                                     text='settings',
                                     font=('Arial', 25, 'bold'),
                                     bg='#BEF8AE',
                                     padx=72,
                                     pady=10,
                                     command=lambda: self.indicate(self.setting_btn, self.setting_page)
                                     )
        self.help_btn = tk.Button(window,
                                  text='help',
                                  font=('Arial', 25, 'bold'),
                                  bg='#BEF8AE',
                                  padx=103,
                                  pady=10,
                                  command=lambda: self.indicate(self.help_btn, self.help_page)
                                  )


        self.server_client.place(x=20, y=50)
        self.connect_btn.place(x=20, y=130)
        self.file_transfer.place(x=20,y=210)
        self.setting_btn.place(x=20, y=290)
        self.help_btn.place(x=20, y=370)

        self.options_frame.place(x=10, y=10)
        self.options_frame.pack_propagate(False)
        self.options_frame.configure(width=300, height=880, background='white')



        # main frame (middle bar)
        self.main_frame = tk.Frame(window)

        self.main_frame.place(x=320, y=10)
        self.main_frame.pack_propagate(False)
        self.main_frame.configure(width=960, height=880)



        # right bar
        self.right_frame = tk.Frame(window)

        self.right_frame.place(x=1290, y=10)
        self.right_frame.pack_propagate(False)
        self.right_frame.configure(width=300, height=880, background='white')


    # server connection
    def server_listen_accept(self, ip_addr, port):
        tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_server.bind((ip_addr, port))
        tcp_server.listen(1)

        client, addr = tcp_server.accept()
        client_username = client.recv(1024).decode()
        client_system_info = client.recv(1024).decode()

    

    # Each time when we change page pressing any button on option(left) bar:
    # 1) we destroy old pages and 
    # 2) we highlit the pressed button by changing its color from #BEF8AE to #63e53f
    def destroy_old_frame(self):
        for frame in self.main_frame.winfo_children():
            frame.destroy()


    def hide_indicators(self):
        self.server_client.config(bg='#BEF8AE')
        self.connect_btn.config(bg='#BEF8AE')
        self.file_transfer.config(bg='#BEF8AE')
        self.setting_btn.config(bg='#BEF8AE')
        self.help_btn.config(bg='#BEF8AE')


    def indicate(self, label, page):
        self.hide_indicators()
        label.config(bg='#63e53f')
        self.destroy_old_frame()
        page()


    # option bar functions

    def server_client_page(self):
        self.server_client_frame = tk.Frame(self.main_frame)

        Login(root)
        

        self.server_client_frame.place(x=0, y=0)
        self.server_client_frame.pack_propagate(False)                                   # False: we can resize the frame and it will not cover all the window automaticlly
        self.server_client_frame.configure(width=960, height=880)


    def connect_page(self):
        self.connect_frame = tk.Frame(self.main_frame)

        # ο κώδικας της Ισμήνης

        self.connect_frame.place(x=0, y=0)
        self.connect_frame.pack_propagate(False)
        self.connect_frame.configure(width=960, height=880)


    def file_transfer_page(self):
        self.file_transfer_frame = tk.Frame(self.main_frame)


        # θα γράψουμε μετά
        self.label_13 = tk.Label(self.main_frame, text='RTFM', font=(5))
        self.label_13.place(x=450, y=300)

        self.file_transfer_frame.place(x=0, y=0)
        self.file_transfer_frame.pack_propagate(False)
        self.file_transfer_frame.configure(width=960, height=880)


    def setting_page(self):
        self.setting_frame = tk.Frame(self.main_frame)

        # θα γράψουμε μετά

        self.setting_frame.place(x=0, y=0)
        self.setting_frame.pack_propagate(False)
        self.setting_frame.configure(width=960, height=880)


    def help_page(self):
        page_frame = tk.Frame(self.main_frame)

        # θα γράψουμε μετά

        page_frame.place(x=0, y=0)
        page_frame.pack_propagate(False)
        page_frame.configure(width=960, height=880)






class Client:

    def __init__(self, window):
        # Deleting old pages(frames)
        for frame in window.winfo_children():
            frame.destroy()


        self.client_frame = tk.Frame(window)

        self.label_welcome = tk.Label(self.client_frame,
                                      text='welcome to client!',
                                      font=('Arial', 30)
                                      )
                                              
        self.label_welcome.pack()

        self.client_frame.pack()
    

    def connect(self, ip_addr, port):
        



run_login = Login(root)


root.mainloop()
