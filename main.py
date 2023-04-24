import tkinter as tk
import socket
import threading
from getpass import getuser
from platform import uname
from time import sleep
import subprocess
import os

# All the buttons color is #85d5fb
btn_color="#85d5fb"
is_user_connected = False


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
        try:
            self.server_socket.bind((ip_addr, int(port)))
        except Exception as error:
            print(error)
        self.server_socket.listen()
        run_login.run_server.listen_btn.config(state='disabled')
        run_login.run_server.print_listening.config(text='Listening...')

        while self.connected and self.server_listen_acccept_bool:
            try:
                self.client, self.addr = self.server_socket.accept()
                print(f"connected {self.addr[0]}, {self.addr[1]}")

                self.client_username = self.client.recv(1024).decode()
                print(self.client_username)

                self.server_listen_accept_bool = False
                self.recv_out_put_thread.start()
                run_login.run_server.command_page()
                root.configure(background='green')
            except:
                self.server_socket.close()
                print("failed , server_listen_accept, while True, except ERROR")
                sleep(3)

        
        

    def send_command(self):
        self.cmnd = run_login.run_server.command_entry.get()
        run_login.run_server.command_entry.delete(0, tk.END)
        if self.connected == True:
            if self.cmnd != "":
                if self.cmnd == "clear" or self.cmnd == "cls":
                    run_login.run_server.output_list.clear()
                    destroy_old_frames(run_login.run_server.inner_frame)
                    run_login.run_server.print_output()
                else:
                    run_login.run_server.output_list.append("------------------------------------------------------------------------------------------------------------------------")
                    run_login.run_server.output_list.append(f'{self.client_username}:> {self.cmnd}')
                    self.client.send(self.cmnd.encode())
        else:
            print("NOT connected!")
        

    def recv_out_put(self):
        while self.connected and self.recv_out_put_bool:
            self.output = self.client.recv(1024).decode()
            run_login.run_server.output_list.append(self.output)
            destroy_old_frames(run_login.run_server.inner_frame)
            run_login.run_server.print_output()
            

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
                self.client_socket.connect((str(ip_addr), int(port)))
                self.client_socket.send(self.client_windows_username.encode())
                self.get_send_command_thread.start()

                self.stop_client_connect_loop = False
                run_login.run_client.print_connected_label.pack()
                run_login.run_client.print_connecting_label.destroy()
                root.configure(background='green')
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
            self.command = self.client_socket.recv(1024).decode()
            if self.command == "exit":
                exit_program()
            elif self.command[0:3] == "cd ":
                os.chdir(self.command[3:])
                self.client_socket.send(os.getcwd().encode())
            else:
                self.output = subprocess.getoutput(self.command)
                if self.output == "" or self.output == None:
                    self.output = "\n"
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
        self.server_port = self.server_port_entry.get()

        if self.server_ip == "":
            run_login.run_server.error_label.config(text='Ip address can not be empty!\nRTFM')
            run_login.run_server.error_label.pack()
        elif self.server_port == "":
            run_login.run_server.error_label.config(text='Port can not be empty!\nRTFM')
            run_login.run_server.error_label.pack()
        elif not is_valid_ip_address(self.server_ip):
            run_login.run_server.error_label.config(text='Invalid ip address\nRTFM')
            run_login.run_server.error_label.pack()


        self.listening_thread = threading.Thread(target=run_login.server.server_listen_accept, args=(self.server_ip, self.server_port))
        self.listening_thread.start()

    def print_output(self):
        for i in self.output_list:
            self.print_output_label = tk.Label(self.inner_frame,
                                        text=i,
                                        font=('Arial', 20),
                                        fg='green',
                                        bg='black',
                                        anchor='nw',
                                        justify='left'
                                        )
            self.print_output_label.pack(fill='both', expand=True)

    # __________All the Pages that the user can access pressing the left bar buttons___________

    # ----------Back page----------
    def choose_user_page(self):
        Login_frame(root)



    # ----------Connection page----------
    def connect_page(self):
        self.indicate(self.connect_btn)
        self.connect_frame = tk.Frame(self.main_frame)
        
        self.connect_frame.place(x=0, y=0)
        self.connect_frame.pack_propagate(False)
        self.connect_frame.configure(width=960, height=880)


        self.listening_label = tk.Label(self.connect_frame,)
        self.server_ip_addr_label = tk.Label(self.connect_frame,
                                             text='IP Addr',
                                             font=("Verdana", 15),
                                             width=0,
                                             height=5,
                                             anchor='s'
                                             )
        self.server_ip_addr_entry = tk.Entry(self.connect_frame,
                                             font=("Verdana", 13),
                                             width=40
                                             )
        self.server_ip_addr_entry.insert(0, get_private_ip_address())
        self.server_port_label = tk.Label(self.connect_frame,
                                          text='PORT',
                                          font=("Verdana", 15),
                                          width=0,
                                          height=2,
                                          anchor='s'
                                          )
        self.server_port_entry = tk.Entry(self.connect_frame,
                                          font=("Verdana", 13),
                                          width=40
                                          )
        self.server_port_entry.insert(0, 8119)
        self.listen_btn = tk.Button(self.connect_frame,
                                    bg="#85d5fb",
                                    text='START',
                                    font="Verdana",
                                    width=5,
                                    height=1,
                                    command=lambda: self.listen_btn_click()
                                    )
        self.print_listening = tk.Label(self.connect_frame,
                                        font="Verdana",
                                        text="",
                                        height=4
                                        )
        self.error_label = tk.Label(self.connect_frame,
                                    font=("Verdana", 15),
                                    text='We show errors here',
                                    bg='red',
                                    fg='white'
                                    )

        self.server_ip_addr_label.pack()
        self.server_ip_addr_entry.pack()
        self.server_port_label.pack()
        self.server_port_entry.pack()
        self.listen_btn.pack()
        self.print_listening.pack()

    
    # ----------Command Line page----------
    def command_page(self):
        self.indicate(self.command_btn)
        self.out_put_frame = tk.Frame(self.main_frame)

        self.output_label = tk.Label(self.main_frame,
                                     text="Output:",
                                     font=('Arial', 15)
                                     )
        self.output_label.place(x=50, y=20)
        
        # ------------------------------scrollbar canvas------------------------------
        self.out_put_frame.place(x=50, y=50)
        self.out_put_frame.pack_propagate(False)
        self.out_put_frame.configure(width=860, height=670, background='black')

        self.canvas = tk.Canvas(self.out_put_frame, background='black')
        self.canvas.pack(fill="both", expand=True)

        self.y_scrollbar = tk.Scrollbar(self.out_put_frame, orient='vertical', command=self.canvas.yview, width=15)
        self.y_scrollbar.pack(side='right', fill='y')
        self.x_scrollbar = tk.Scrollbar(self.out_put_frame, orient='horizontal', command=self.canvas.xview, width=15)
        self.x_scrollbar.pack(side='bottom', fill='x')

        self.canvas.configure(xscrollcommand=self.x_scrollbar.set, yscrollcommand=self.y_scrollbar.set)

        self.inner_frame = tk.Frame(self.canvas, background='black')

        self.output_list = []

        self.canvas.create_window((0,0), window=self.inner_frame, anchor='nw')

        def on_canvas_resize(event):
            self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        self.canvas.bind("<Configure>", on_canvas_resize)

        def on_inner_frame_resize(event):
            self.canvas.itemconfigure(inner_frame_window, width=event.width)
        self.inner_frame.bind("configure>", on_inner_frame_resize)
        inner_frame_window = self.canvas.create_window((0,0), window=self.inner_frame, anchor='nw')
        # ---------------------------------------------------------------------------

        self.print_new_command_label = tk.Label(self.main_frame,
                                                text='New Command:',
                                                font=('Arial', 15)
                                                )
        self.command_entry = tk.Entry(self.main_frame,
                                      font=('Arial', 20),
                                      fg='green',
                                      bg='black',
                                      width=57,
                                      )
        self.send = tk.Button(self.main_frame,
                              text="Send",
                              command= lambda: run_login.server.send_command()
                              )
        
        self.print_new_command_label.place(x=50, y=730)
        self.command_entry.place(x=50, y=760)
        self.send.place(x=450, y=825)


    # ----------Transfer page----------
    def file_transfer_page(self):
        self.indicate(self.file_transfer_btn)
        self.file_transfer_frame = tk.Frame(self.main_frame)

        self.file_transfer_frame.place(x=0, y=0)
        self.file_transfer_frame.pack_propagate(False)
        self.file_transfer_frame.configure(width=960, height=880)


        # θα γράψουμε μετά
        self.rtfm_label = tk.Label(self.main_frame, text='RTFM', font=(5))
        self.rtfm_label.place(x=450, y=300)


    # ----------Setting page----------
    def setting_page(self):
        self.indicate(self.setting_btn)
        self.setting_frame = tk.Frame(self.main_frame)

        self.setting_frame.place(x=0, y=0)
        self.setting_frame.pack_propagate(False)
        self.setting_frame.configure(width=960, height=880)

        # θα γράψουμε μετά


    # ----------Help page----------
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


        # ----------options bar (left bar)----------
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
    # ----------Back page----------
    def cln_choose_user_page(self):
        Login_frame(root)

    # ----------Connection page----------
    def cln_connect_page(self):
        self.indicate(self.cln_connect_btn)
        self.cln_connect_frame = tk.Frame(self.cln_main_frame)
        self.cln_connect_frame.pack()

        self.client_ip_addr_label = tk.Label(self.cln_main_frame,
                                             text='SERVER-IP',
                                             font=("Verdana", 15),
                                             width=0,
                                             height=5,
                                             anchor="s"
                                             )
        self.client_ip_addr_entry = tk.Entry(self.cln_main_frame,
                                             font=("Verdana", 13),
                                             width=40
                                             )
        self.client_ip_addr_entry.insert(0, get_private_ip_address())
        self.client_port_label = tk.Label(self.cln_main_frame,
                                          text='PORT',
                                          font=("Verdana", 15),
                                          width=0,
                                          height=2,
                                          anchor="s"
                                          )
        self.client_port_entry = tk.Entry(self.cln_main_frame,
                                          font=("Verdana", 13),
                                          width=40
                                          )
        self.client_port_entry.insert(0, 8119)
        self.client_connect_server = tk.Button(self.cln_main_frame,
                                               bg="#85d5fb",
                                               text='START',
                                               font="Verdana",
                                               width=5,
                                               height=1,
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

    # ----------Help page----------
    def cln_help_page(self):
        self.indicate(self.cln_help_btn)
        self.cln_help_frame = tk.Frame(self.cln_main_frame)
        self.cln_help_frame.pack()






def destroy_old_frames(frame):
        for frame in frame.winfo_children():
            frame.destroy()


def get_private_ip_address():
    try:
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_socket.connect(('8.8.8.8', 80))
        ip_address = temp_socket.getsockname()[0]
    except socket.error:
        ip_address = '127.0.0.1'
    finally:
        temp_socket.close()
    return ip_address


def is_valid_ip_address(ip_address):
    segments = ip_address.split(".")
    if len(segments) != 4:
        return False
    for segment in segments:
        if not segment.isdigit():
            return False
        if int(segment) < 0 or int(segment) > 255:
            return False
    return True


def exit_program():
    root.destroy()
    exit()




root = tk.Tk()
root.geometry("1600x900")
root.configure(background='red')
root.title("Matin")

# Runnig program 
run_login = Login_frame(root)


root.mainloop()
