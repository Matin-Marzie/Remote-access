import tkinter as tk
import socket
import threading
from getpass import getuser
from platform import uname
from time import sleep

root = tk.Tk()
root.geometry("1600x900")
root.configure(background='#000000')
root.title("Matin")

'''
In this program we have three objects:
    1)Login             The user will choose client or server, Login will navigate the user to server or client
    2)Server            
    3)Client
'''

def destroy_old_frames(frame):
        for frame in frame.winfo_children():
            frame.destroy()



class Login:

    def __init__(self, window):

        destroy_old_frames(window)
        
        # Frame
        self.login_frame = tk.Frame(window)
        
        self.login_frame.pack()
        
        # Content
        my_color="#85d5fb"

        self.choose_label = tk.Label(self.login_frame,
                                text="CHOOSE USER",font=("Verdana"),width=90,height=32,bg="white"
                                     )
        self.server_btn = tk.Button(self.login_frame,
                               text="SERVER",font="Verdana",bg=my_color,fg="black",width=90,height=2,
                               command=self.choosen_server
                               )
        self.client_btn = tk.Button(self.login_frame,
                               text="CLIENT",font="Verdana",bg=my_color,fg="black",width=90,height=2,
                               command=self.choosen_client
                               )

        # Appending our content
        self.choose_label.pack()
        self.server_btn.pack()
        self.client_btn.pack()

    # if user chooses server
    def choosen_server(self):
        run_server = Server(root)
        run_server.connect_page()                       # we display connect_page() for default
        run_server.connect_btn.config(bg='#0080FF')     # also highlit it's button #00BFFF #0080FF

    # if user chooses client
    def choosen_client(self):
        run_client = Client(root)
        run_client.cln_connect_page()
        run_client.cln_connect_btn.config(bg='#0080FF') 




class Server():

    def __init__(self, window):

        destroy_old_frames(window)

        # Frames
        self.options_frame = tk.Frame(window)               # Left bar (options frame)
        self.main_frame = tk.Frame(window)                  # Middle bar
        self.right_frame = tk.Frame(window)                 # right bar 

        #showing frame
        self.options_frame.place(x=10, y=10)
        self.options_frame.pack_propagate(False)            # False: we can resize the frame and it will not cover all the window automaticlly
        self.options_frame.configure(width=300, height=880, background='white')

        self.main_frame.place(x=320, y=10)
        self.main_frame.pack_propagate(False)
        self.main_frame.configure(width=960, height=880)

        self.right_frame.place(x=1290, y=10)
        self.right_frame.pack_propagate(False)
        self.right_frame.configure(width=300, height=880, background='white')


        # Left bar (option bar)
        self.choose_user_btn = tk.Button(self.options_frame,
                                       text='Back',
                                       font=('Verdana', 25),
                                       bg='#85d5fb',
                                       padx=20,width=10,height=1,
                                       pady=1,anchor="n",
                                       command=lambda: self.indicate(self.choose_user_btn, self.choose_user_page)
                                       )
        self.connect_btn = tk.Button(self.options_frame,
                                     text='Connection',
                                     font=('Verdana', 25),
                                     bg='#85d5fb',
                                     padx=20,width=10,height=1,
                                     pady=1,anchor="n",
                                     command=lambda: self.indicate(self.connect_btn, self.connect_page)
                                     )
        self.command_btn = tk.Button(self.options_frame,
                                     text='Command Line',
                                     font=('Verdana', 25),
                                     bg='#85d5fb',
                                     padx=20,width=10,height=1,
                                     pady=1,anchor="n",
                                     command=lambda: self.indicate(self.command_btn, self.command_page)
                                     )
        self.file_transfer = tk.Button(self.options_frame,
                                       text='Transfer',
                                       font=('Verdana', 25),
                                       bg='#85d5fb',
                                       padx=20,width=10,height=1,
                                       pady=1,anchor="n",
                                       command=lambda: self.indicate(self.file_transfer, self.file_transfer_page)
                                       )
        self.setting_btn = tk.Button(self.options_frame,
                                     text='Setting',
                                     font=('Verdana', 25),
                                     bg='#85d5fb',
                                     padx=20,width=10,height=1,
                                     pady=1,anchor="n",
                                     command=lambda: self.indicate(self.setting_btn, self.setting_page)
                                     )
        self.help_btn = tk.Button(self.options_frame,
                                  text='Help',
                                  font=('Verdana', 25),
                                  bg='#85d5fb',
                                  padx=20,width=10,height=1,
                                  pady=1,anchor="n",
                                  command=lambda: self.indicate(self.help_btn, self.help_page)
                                  )

        # Showing option bar
        self.choose_user_btn.place(x=10, y=50)
        self.connect_btn.place(x=10, y=130)
        self.command_btn.place(x=10, y=210)
        self.file_transfer.place(x=10,y=290)
        self.setting_btn.place(x=10, y=370)
        self.help_btn.place(x=10, y=450)





    # Each time when we change page pressing any button on option(left) bar:
    # 1) we destroy old pages on main frame
    # 2) we highlit the pressed button by changing its color from #00BFFF to #63e53f #00BFFF #0080FF
    # 3) display the pressed button page

    def hide_indicator(self):
        self.choose_user_btn.config(bg='#85d5fb')
        self.connect_btn.config(bg='#85d5fb')
        self.command_btn.config(bg='#85d5fb')
        self.file_transfer.config(bg='#85d5fb')
        self.setting_btn.config(bg='#85d5fb')
        self.help_btn.config(bg='#85d5fb')


    def indicate(self, label, page):
        self.hide_indicator()
        label.config(bg='#0080FF')
        destroy_old_frames(self.main_frame)
        page()


    # printing listening...
    def print_listening(self):
        while True:
            self.listening_label.config(text='listening.')
            sleep(1)
            self.listening_label.config(text='listening..')
            sleep(1)
            self.listening_label.config(text='listening...  ')
            sleep(1)


    #########################################################################################
    # server connection
    def server_listen_accept(self, ip_addr, port):
        self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server.bind((ip_addr, int(port)))
        self.tcp_server.listen(1)
        threading.Thread(target=self.print_listening, args=()).start()
        while True:
            try:
                client, addr = self.tcp_server.accept()
                self.client_username = client.recv(1024).decode()
                self.client_os = client.recv(1024).decode()
                print(self.client_username)
                print("\n")
                print(self.client_os)
            except:
                self.tcp_server.close()
                print("failed 1")

    def listen_btn_click(self):
        server_ip = self.server_ip_addr_entry.get()
        server_port = self.server_port_entry.get()
        threading.Thread(target=self.server_listen_accept, args=(server_ip, server_port)).start()

        
    #########################################################################################


    # Pages

    def choose_user_page(self):
        Login(root)
        


    def connect_page(self):
        self.connect_frame = tk.Frame(self.main_frame)
        
        self.connect_frame.place(x=0, y=0)
        self.connect_frame.pack_propagate(False)
        self.connect_frame.configure(width=960, height=880)


        self.listening_label = tk.Label(self.main_frame,)
        self.server_ip_addr_label = tk.Label(self.main_frame, text='IP Addr',font="Verdana",width=0,height=0,anchor="ne")
        self.server_ip_addr_entry = tk.Entry(self.main_frame,width=50)
        self.server_port_label = tk.Label(self.main_frame, text='PORT',font="Verdana",width=0,height=0,anchor="ne")
        self.server_port_entry = tk.Entry(self.main_frame,width=50)
        self.listen_btn = tk.Button(self.main_frame,bg="#85d5fb", text='START',font="Verdana",width=0,height=0,anchor="center",command=self.listen_btn_click)
        self.server_reset_btn = tk.Button(self.main_frame, text='reset')

        self.listening_label.pack()
        self.server_ip_addr_label.pack()
        self.server_ip_addr_entry.pack()
        self.server_port_label.pack()
        self.server_port_entry.pack()
        self.listen_btn.pack()

    
    def command_page(self):
        self.command_frame = tk.Frame(self.main_frame)
        self.command_frame.pack()

        self.command_entry = tk.Entry(self.main_frame,
                                      font=('Arial', 25),
                                      fg='green',
                                      bg='black',
                                      width=45,
                                      )
        self.output_label = tk.Label(self.main_frame,
                                     text="output:\t\t\t\n\n@root:~$ cd Desktop/remote-access/\n@root:~/Desktop/remote-access$ ssh root@82.180.173.157\nroot@82.180.173.157's\npassword: \nroot@encryption:~# nc -lvp 443\n\n\n\n\n\n\n\n\n\n\n",
                                     font=('Arial', 20),
                                     fg='green',
                                     bg='black',
                                     width=57,
                                     height=22
                                     )
        
        self.command_entry.place(x=50, y=760)
        self.output_label.place(x=50, y=10)


    def file_transfer_page(self):
        self.file_transfer_frame = tk.Frame(self.main_frame)

        self.file_transfer_frame.place(x=0, y=0)
        self.file_transfer_frame.pack_propagate(False)
        self.file_transfer_frame.configure(width=960, height=880)


        # θα γράψουμε μετά
        self.label_13 = tk.Label(self.main_frame, text='RTFM', font=(5))
        self.label_13.place(x=450, y=300)


    def setting_page(self):
        self.setting_frame = tk.Frame(self.main_frame)

        self.setting_frame.place(x=0, y=0)
        self.setting_frame.pack_propagate(False)
        self.setting_frame.configure(width=960, height=880)

        # θα γράψουμε μετά


    def help_page(self):
        page_frame = tk.Frame(self.main_frame)

        page_frame.place(x=0, y=0)
        page_frame.pack_propagate(False)
        page_frame.configure(width=960, height=880)
        
        # θα γράψουμε μετά






class Client:

    def __init__(self, window):

        destroy_old_frames(window)

        # Frames
        self.cln_options_frame = tk.Frame(window)
        self.cln_main_frame = tk.Frame(window)
        self.cln_right_frame = tk.Frame(window)

        self.cln_options_frame.place(x=10, y=10)
        self.cln_options_frame.pack_propagate(False)
        self.cln_options_frame.configure(width=300, height=880, background='white')

        self.cln_main_frame.place(x=320, y=10)
        self.cln_main_frame.pack_propagate(False)
        self.cln_main_frame.configure(width=960, height=880)

        self.cln_right_frame.place(x=1290, y=10)
        self.cln_right_frame.pack_propagate(False)
        self.cln_right_frame.configure(width=300, height=880, background='white')


        # options bar (left bar)
        self.cln_choose_user_btn = tk.Button(window,
                                       text='Back',
                                       font=('Verdana', 25),
                                       bg='#85d5fb',
                                       padx=20,width=10,height=1,
                                       pady=1,anchor="n",
                                       command=lambda: self.indicate(self.cln_choose_user_btn, self.cln_choose_user_page)
                                       )
        self.cln_connect_btn = tk.Button(window,
                                     text='Connect',
                                     font=('Verdana', 25),
                                     bg='#85d5fb',
                                     padx=20,width=10,height=1,
                                     pady=1,anchor="n",
                                     command=lambda: self.indicate(self.cln_connect_btn, self.cln_connect_page)
                                     )
        self.cln_help_btn = tk.Button(window,
                                  text='Help',
                                  font=('Verdana', 25),
                                  bg='#85d5fb',
                                  padx=20,width=10,height=1,
                                  pady=1,anchor="n",
                                  command=lambda: self.indicate(self.cln_help_btn, self.cln_help_page)
                                  )
        
        self.client_windows_username = getuser()
        self.client_os_info = uname()
        

        self.cln_choose_user_btn.place(x=20, y=50)
        self.cln_connect_btn.place(x=20, y=130)
        self.cln_help_btn.place(x=20, y=210)


    def hide_indicator(self):
        self.cln_choose_user_btn.config(bg='#85d5fb')
        self.cln_connect_btn.config(bg='#85d5fb')
        self.cln_help_btn.config(bg='#85d5fb')


    def indicate(self, label, page):
        self.hide_indicator()
        label.config(bg='#0080FF') #00BFFF #0080FF
        destroy_old_frames(self.cln_main_frame)
        page()



    # Pages
    def cln_choose_user_page(self):
        Login(root)

    def cln_connect_page(self):
        self.cln_connect_frame = tk.Frame(self.cln_main_frame)
        self.cln_connect_frame.pack()

        self.client_ip_addr_label = tk.Label(self.cln_main_frame, text='SERVER-IP',font="Verdana",width=0,height=0,anchor="ne")
        self.client_ip_addr_entry = tk.Entry(self.cln_main_frame,width=50)
        self.client_port_label = tk.Label(self.cln_main_frame, text='PORT',font="Verdana",width=0,height=0,anchor="ne")
        self.client_port_entry = tk.Entry(self.cln_main_frame,width=50)
        self.client_connect_server = tk.Button(self.cln_main_frame,bg="#85d5fb", text='START',font="Verdana",width=0,height=0,anchor="center", command=self.client_connect_click)

        self.client_ip_addr_label.pack()
        self.client_ip_addr_entry.pack()
        self.client_port_label.pack()
        self.client_port_entry.pack()
        self.client_connect_server.pack()

    def cln_help_page(self):
        self.cln_help_frame = tk.Frame(self.cln_main_frame)
        self.cln_help_frame.pack()


    #######################################################################
    # client connection
    def client_connect(self, ip_addr, port):
        tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            tcp_client.connect((ip_addr, int(port)))
            tcp_client.send(self.client_windows_username.encode())
            tcp_client.send(str(self.client_os_info).encode())
        except:
            print("client couldn't connecct!")
        
    
    def client_connect_click(self):
        client_ip = self.client_ip_addr_entry.get()
        client_port = self.client_port_entry.get()
        self.client_connection_thread = threading.Thread(target=self.client_connect, args=(client_ip, client_port)).start()

    #######################################################################

# Runnig program 
run_login = Login(root)


root.mainloop()

