import tkinter as tk
import socket
import threading
from getpass import getuser
from platform import uname
from time import sleep
import subprocess
import os

btn_color="#85d5fb"



# ----------server-socket----------
class Server():

    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.voice_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.recv_out_put_thread = threading.Thread(target=self.recv_out_put, args=())

        self.connected = True
        self.server_listen_acccept_bool = True
        self.recv_out_put_bool = True


    def server_listen_accept(self, ip_addr, port):
        self.server_socket.bind((ip_addr, port))
        self.server_socket.listen()

        run_login.run_server.print_listening.pack()
        while self.connected and self.server_listen_acccept_bool:
            try:
                self.client, self.addr = self.server_socket.accept()
                print(f"connected {self.addr[0]}, {self.addr[1]}")
                client_system_info = self.client.recv(1024).decode()
                print(client_system_info)
                self.server_listen_accept_bool = False
                self.recv_out_put_thread.start()
            except:
                self.server_socket.close()
                print("failed , server_listen_accept, while True, except ERROR")
                
        Server_frame(root).command_page()

    def send_command(self, cmnd):
        if self.connected == True:
            self.client.send(cmnd.encode())
        else:
            print("NOT connected!")
        

    def recv_out_put(self):
        while self.connected and self.recv_out_put_bool:
            self.output = self.client.recv(1024).decode()
            run_login.run_server.output_label.config(text=self.output)


    def voice_socket():
        pass









# ----------client-socket----------
class Client():
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.get_send_command_thread = threading.Thread(target=self.get_send_command, args=())

        self.client_windows_username = getuser()
        self.connected = True
        self.stop_client_connect_loop = True
        self.stop_get_send_command_loop = True

    def client_connect(self, ip_addr, port):
        while self.connected and self.stop_client_connect_loop:
            try:
                self.client_socket.connect((ip_addr, int(port)))
                self.client_socket.send(self.client_windows_username.encode())
                self.get_send_command_thread.start()

                self.stop_client_connect_loop = False
                run_login.run_client.print_connected_label.pack()
                run_login.run_client.print_connecting_label.destroy()
            except:
                run_login.run_client.print_connecting_label.pack()
                sleep(1)
                run_login.run_client.print_connecting_label.config(text="Connecting.")
                sleep(1)
                run_login.run_client.print_connecting_label.config(text="Connecting..")
                sleep(1)
                run_login.run_client.print_connecting_label.config(text="Connecting...")
                sleep(1)

    def get_send_command(self):
        while self.connected and self.stop_get_send_command_loop:
            self.command = self.client_socket.recv(1024)

            if self.command == "exit":
                exit()
            elif self.command[:2] == "cd":
                os.chdir(self.command[:2])
                self.client_socket.send(os.getcwd().encode())
            else:

                self.output = subprocess.getoutput(self.command.decode())
                if self.output == "" or self.output == None:
                    self.output = "Error"
                    self.client_socket.send(self.output.encode())
                else:
                    self.client_socket.send(self.output.encode())




# ----------login-window----------
class Login_frame():
    
    def __init__(self, window):

        destroy_old_frames(window)
        
        # Frame
        self.login_frame = tk.Frame(window)
        
        self.login_frame.pack()
        
        # Content

        self.choose_label = tk.Label(self.login_frame,
                                text="CHOOSE USER",font=("Verdana"),width=90,height=32,bg="white"
                                     )
        self.server_btn = tk.Button(self.login_frame,
                               text="SERVER",font="Verdana",bg=btn_color,fg="black",width=90,height=2,
                               command=self.choosen_server
                               )
        self.client_btn = tk.Button(self.login_frame,
                               text="CLIENT",font="Verdana",bg=btn_color,fg="black",width=90,height=2,
                               command=self.choosen_client
                               )

        # Appending our content
        self.choose_label.pack()
        self.server_btn.pack()
        self.client_btn.pack()
        

    # if user chooses server
    def choosen_server(self):
        self.run_server = Server_frame(root)
        self.run_server.connect_page()                       # we display connect_page() for default
        self.run_server.connect_btn.config(bg='#0080FF')     # also highlit it's button #00BFFF #0080FF

        self.server = Server()

    # if user chooses client
    def choosen_client(self):
        self.run_client = Client_frame(root)
        self.run_client.cln_connect_page()
        self.run_client.cln_connect_btn.config(bg='#0080FF') 

        self.client = Client()





# ----------server-window----------
class Server_frame():
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
                                       command=lambda: (self.choose_user_page())
                                       )
        self.connect_btn = tk.Button(self.options_frame,
                                     text='Connection',
                                     font=('Verdana', 25),
                                     bg='#85d5fb',
                                     padx=20,width=10,height=1,
                                     pady=1,anchor="n",
                                     command=lambda: (self.connect_page())
                                     )
        self.command_btn = tk.Button(self.options_frame,
                                     text='Command Line',
                                     font=('Verdana', 25),
                                     bg='#85d5fb',
                                     padx=20,width=10,height=1,
                                     pady=1,anchor="n",
                                     command=lambda: (self.command_page())
                                     )
        self.file_transfer_btn = tk.Button(self.options_frame,
                                       text='Transfer',
                                       font=('Verdana', 25),
                                       bg='#85d5fb',
                                       padx=20,width=10,height=1,
                                       pady=1,anchor="n",
                                       command=lambda: (self.file_transfer_page())
                                       )
        self.setting_btn = tk.Button(self.options_frame,
                                     text='Setting',
                                     font=('Verdana', 25),
                                     bg='#85d5fb',
                                     padx=20,width=10,height=1,
                                     pady=1,anchor="n",
                                     command=lambda: (self.setting_page())
                                     )
        self.help_btn = tk.Button(self.options_frame,
                                  text='Help',
                                  font=('Verdana', 25),
                                  bg='#85d5fb',
                                  padx=20,width=10,height=1,
                                  pady=1,anchor="n",
                                  command=lambda: (self.help_page())
                                  )

        # Showing option bar
        self.choose_user_btn.place(x=10, y=50)
        self.connect_btn.place(x=10, y=130)
        self.command_btn.place(x=10, y=210)
        self.file_transfer_btn.place(x=10,y=290)
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
        self.file_transfer_btn.config(bg='#85d5fb')
        self.setting_btn.config(bg='#85d5fb')
        self.help_btn.config(bg='#85d5fb')


    def indicate(self, label):
        self.hide_indicator()
        label.config(bg='#0080FF')
        destroy_old_frames(self.main_frame)


    def listen_btn_click(self):
        self.server_ip = self.server_ip_addr_entry.get()
        self.server_port = int(self.server_port_entry.get())

        self.listen_btn.config(state='disabled')

        self.listening_thread = threading.Thread(target=run_login.server.server_listen_accept, args=(self.server_ip, self.server_port))
        self.listening_thread.start()




    # Pages

    def choose_user_page(self):
        Login_frame(root)



    def connect_page(self):
        self.indicate(self.connect_btn)
        self.connect_frame = tk.Frame(self.main_frame)
        
        self.connect_frame.place(x=0, y=0)
        self.connect_frame.pack_propagate(False)
        self.connect_frame.configure(width=960, height=880)


        self.listening_label = tk.Label(self.main_frame,)
        self.server_ip_addr_label = tk.Label(self.main_frame,
                                             text='IP Addr',
                                             font="Verdana",
                                             width=0,height=0,
                                             anchor="ne"
                                             )
        self.server_ip_addr_entry = tk.Entry(self.main_frame,
                                             width=50
                                             )
        self.server_ip_addr_entry.insert(0, "127.0.0.1")
        self.server_port_label = tk.Label(self.main_frame,
                                          text='PORT',
                                          font="Verdana",
                                          width=0,height=0,
                                          anchor="ne"
                                          )
        self.server_port_entry = tk.Entry(self.main_frame,
                                          width=50)
        self.server_port_entry.insert(0, 8119)
        self.listen_btn = tk.Button(self.main_frame,
                                    bg="#85d5fb",
                                    text='START',
                                    font="Verdana",width=0,height=0,anchor="w",command=lambda: self.listen_btn_click())
        self.print_listening = tk.Label(self.main_frame,
                                        font="Verdana",
                                        text="Listening"
                                        )

        self.server_ip_addr_label.pack()
        self.server_ip_addr_entry.pack()
        self.server_port_label.pack()
        self.server_port_entry.pack()
        self.listen_btn.pack()

    
    def command_page(self):
        self.indicate(self.command_btn)
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
        
    
        self.send = tk.Button(self.main_frame,
                              text="Send",
                              command= lambda: run_login.server.send_command(self.command_entry.get())
                              )
        
        self.command_entry.place(x=50, y=760)
        self.output_label.place(x=50, y=10)
        self.send.place(x=450, y=825)


    def file_transfer_page(self):
        self.indicate(self.file_transfer_btn)
        self.file_transfer_frame = tk.Frame(self.main_frame)

        self.file_transfer_frame.place(x=0, y=0)
        self.file_transfer_frame.pack_propagate(False)
        self.file_transfer_frame.configure(width=960, height=880)


        # θα γράψουμε μετά
        self.rtfm_label = tk.Label(self.main_frame, text='RTFM', font=(5))
        self.rtfm_label.place(x=450, y=300)


    def setting_page(self):
        self.indicate(self.setting_btn)
        self.setting_frame = tk.Frame(self.main_frame)

        self.setting_frame.place(x=0, y=0)
        self.setting_frame.pack_propagate(False)
        self.setting_frame.configure(width=960, height=880)

        # θα γράψουμε μετά


    def help_page(self):
        self.indicate(self.help_btn)
        page_frame = tk.Frame(self.main_frame)

        page_frame.place(x=0, y=0)
        page_frame.pack_propagate(False)
        page_frame.configure(width=960, height=880)
        
        # θα γράψουμε μετά



# ----------client-window----------
class Client_frame():
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
                                       command=lambda: self.cln_choose_user_page()
                                       )
        self.cln_connect_btn = tk.Button(window,
                                     text='Connect',
                                     font=('Verdana', 25),
                                     bg='#85d5fb',
                                     padx=20,width=10,height=1,
                                     pady=1,anchor="n",
                                     command=lambda: self.cln_connect_page()
                                     )
        self.cln_help_btn = tk.Button(window,
                                  text='Help',
                                  font=('Verdana', 25),
                                  bg='#85d5fb',
                                  padx=20,width=10,height=1,
                                  pady=1,anchor="n",
                                  command=lambda: self.cln_help_page()
                                  )
        
        

        self.cln_choose_user_btn.place(x=20, y=50)
        self.cln_connect_btn.place(x=20, y=130)
        self.cln_help_btn.place(x=20, y=210)


    def hide_indicator(self):
        self.cln_choose_user_btn.config(bg='#85d5fb')
        self.cln_connect_btn.config(bg='#85d5fb')
        self.cln_help_btn.config(bg='#85d5fb')


    def indicate(self, label):
        self.hide_indicator()
        label.config(bg='#0080FF')
        destroy_old_frames(self.cln_main_frame)


    def client_connect_click(self):
        client_ip = self.client_ip_addr_entry.get()
        client_port = self.client_port_entry.get()
        self.client_connect_server.config(state='disabled')

        self.client_connection_thread = threading.Thread(target=run_login.client.client_connect, args=(client_ip, client_port))
        self.client_connection_thread.start()

    

    # Pages
    def cln_choose_user_page(self):
        Login_frame(root)

    def cln_connect_page(self):
        self.indicate(self.cln_connect_btn)
        self.cln_connect_frame = tk.Frame(self.cln_main_frame)
        self.cln_connect_frame.pack()

        self.client_ip_addr_label = tk.Label(self.cln_main_frame,
                                             text='SERVER-IP',
                                             font="Verdana",
                                             width=0,
                                             height=0,
                                             anchor="ne"
                                             )
        self.client_ip_addr_entry = tk.Entry(self.cln_main_frame,
                                             width=50
                                             )
        self.client_ip_addr_entry.insert(0, "127.0.0.1")
        self.client_port_label = tk.Label(self.cln_main_frame,
                                          text='PORT',
                                          font="Verdana",
                                          width=0,
                                          height=0,
                                          anchor="ne"
                                          )
        self.client_port_entry = tk.Entry(self.cln_main_frame,
                                          width=50
                                          )
        self.client_port_entry.insert(0, 8119)
        self.client_connect_server = tk.Button(self.cln_main_frame,
                                               bg="#85d5fb",
                                               text='START',
                                               font="Verdana",
                                               width=0,
                                               height=0,
                                               anchor="center",
                                               command=lambda: self.client_connect_click()
                                               )
        self.print_connecting_label = tk.Label(self.cln_main_frame,
                                                font="Verdana",
                                                text="Connecting"
                                                )
        self.print_connected_label = tk.Label(self.cln_main_frame,
                                                font="Verdana",
                                                text="Connected"
                                                )
        
        self.client_ip_addr_label.pack()
        self.client_ip_addr_entry.pack()
        self.client_port_label.pack()
        self.client_port_entry.pack()
        self.client_connect_server.pack()

    def cln_help_page(self):
        self.indicate(self.cln_help_btn)
        self.cln_help_frame = tk.Frame(self.cln_main_frame)
        self.cln_help_frame.pack()



def destroy_old_frames(frame):
        for frame in frame.winfo_children():
            frame.destroy()
        



root = tk.Tk()
root.geometry("1600x900")
root.configure(background='#000000')
root.title("Matin")

# Runnig program 
run_login = Login_frame(root)



root.mainloop()
