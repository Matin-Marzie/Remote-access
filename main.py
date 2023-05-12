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
# All the libraries are build in with python, except the 'pyscreenshot', that is why we try to install it.
try:
    import pyscreenshot
except:
    try:
        subprocess.run(['pip', "install", 'pyscreenshot'])
    except:
        pass

# All the buttons colors:
button_color = '#85d5fb'
pressed_button_color = '#0080FF'

#font
font_name = 'Verdana'


# ____________________server-socket____________________
# Backend of our server-GUI
class Server():

    def __init__(self):
        # This socket is for creating connection with client, after the connection, all the commands of the Command Line will be send with this socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # With this socket we check the connecton between client and server
        self.ping_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


        # We stop the threads using boolean variables, indeed we break the loop of the function  
        self.recv_out_put_bool = True
        self.accept_client_bool = True
        self.capture_ping_bool = True

        # If the user, from other pages(ex.Command Line) wants to return to the Connection page, the information will be shoen depending on the connection state
        self.is_client_connected = False
        self.is_server_listening = False

        self.client_ping = None
        self.client = None


    # After the connection, the client sends a message("ping"), server captures that 'ping' and sends back a message("pong"), this will happen each 3 seconds
    # with this algorithm we know if the client and server is connected or if there is an internet problem, we can handle that kind of error!
    # if the server does not recieves any ping from the client, after 6 seconds, the server disconnects the client
    def capture_ping(self, ip_addr, port):
        # If the server start listening with out a problem, self.accept_client_bool will be True
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
        # After the server starts listening successfully:
        if self.accept_client_bool:
            run_login.run_server.listen_btn.config(state='disabled')
            run_login.run_server.print_server_connection_state.config(text='Listening...')
            if run_login.run_server.socket_error.winfo_exists():
                run_login.run_server.socket_error.destroy()

        while self.accept_client_bool:
            # Here the server accepts the client for the first time or we are waiting for the client to reconnect
            read, _, _ = select.select([self.ping_socket], [], [], 0.5)
            if self.ping_socket in read:
                self.client_ping, self.addr_ping = self.ping_socket.accept()
                self.client, self.addr = self.server_socket.accept()

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

            #in this loop we recieve the ping and send pong, in other cases we close the clients and stop the loop and we wait for the clients to reconnect!
            while self.capture_ping_bool:
                readable, _, _ = select.select([self.client_ping], [], [], 1)
                if self.client_ping in readable:
                    try:
                        self.ping = self.client_ping.recv(1024)
                    except socket.error as e:
                        if str(e) == "[Errno 9] Bad file descriptor":
                            continue

                    if self.ping == b'ping':
                        try:
                            self.client_ping.sendall(b'pong')
                            self.is_client_connected = True
                            root.configure(background='green')
                            started_time = time()
                        except:
                            self.client_ping.close()
                            self.client.close()
                            self.client_ping = None
                            self.is_server_listening = True
                            self.is_client_connected = False
                            run_login.run_server.addr_0_label.config(text="")
                            run_login.run_server.addr_1_label.config(text="")
                            run_login.run_server.right_bar_client_label.config(text="Disconnected!")

                            break

                    elif(int(time() - started_time)) > 5:
                        self.client_ping.close()
                        self.client.close()
                        self.client_ping = None
                        self.is_server_listening = True
                        self.is_client_connected = False
                        run_login.run_server.addr_0_label.config(text="")
                        run_login.run_server.addr_1_label.config(text="")
                        run_login.run_server.right_bar_client_label.config(text="Disconnected!")

                        break

                    # After the 3 seconds, which means that we have not recved and pink, we just change the background color to red
                    elif(int(time() - started_time)) > 2:
                        root.configure(background='red')
                        self.is_server_listening = True

                    else:
                        pass

        
    # With this fuction we send our command to the client
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

        
            
            
        
    # After we send the commands, we recieve the output with this function
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
                    # in the case of screenshot command we recieve the image of the screenshot of the client
                    if self.output == "screenshot--*#($)&":
                        self.client.sendall(b'ok')
                        data = self.client.recv(1024).decode()
                        try:
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
                            # After we recieve the screenshot image we open it automaticlly
                            subprocess.run(['xdg-open', 'victim-screenshot.png'])
                        except:
                            pass
                        if data == "not ok":
                            run_login.run_server.output_list.insert(tk.END, "can't screenshot")

                    # in the case of showfile command, we recieve the file from the client and save to the same directory with the program
                    elif self.output == "showfile--*#($)&":
                        self.client.sendall(b'ok')
                        data = self.client.recv(1024).decode()
                        if data != "not ok":
                            self.file_name, self.file_size = data.split('|')
                            self.file_size = int(self.file_size)
                            self.client.sendall(b'ok')

                            with open(f"recv-{self.file_name}", 'wb') as file:
                                while self.file_size > 0:
                                    data = self.client.recv(min(self.file_size, 4096))
                                    file.write(data)
                                    self.file_size -= len(data)
                                    if not data:
                                        break
                                self.client.sendall(b'ok')
                            subprocess.run(['xdg-open', f"recv-{self.file_name}"])
                        else:
                            run_login.run_server.output_list.insert(tk.END, "ERROR")
                            run_login.run_server.output_list.yview(tk.END)


                    else:
                        # Because the tkinter.Listbox doesn't read '\n' we have to seperate them manually
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
# Backend of client-GUI
class Client():

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ping_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.client_windows_username = getuser()

        # Connection state of client
        self.is_client_connecting = False
        self.is_connected_to_server = False

        # Boolean variables to stop the threads 
        self.client_connecting_bool = True
        self.cln_send_ping_bool = False
        self.get_send_command_bool = True

    # In this function we connect to the server and start sending 'ping' each 3 seconds
    def client_connect(self, ip_addr, port, time=3):
        self.is_client_connecting = True

        while self.client_connecting_bool:
            try:
                self.ping_socket.connect((ip_addr, int(port)))
                self.client_socket.connect((ip_addr, (int(port)+1 )))

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

                # If there is no server to connect, we wait for 2 seconds and try again to connect
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

    # This function of client, recieves the commands and execute them using subproccess and send backs to the server the output
    def get_send_command(self):
        while self.get_send_command_bool:
            if self.client_socket.fileno() != -1:
                readable, _, _ = select.select([self.client_socket], [], [], 0.5)
                if self.client_socket in readable:
                    try:
                        self.command = self.client_socket.recv(1024).decode()

                        # If the command is exit, we close the program
                        if self.command == "exit":
                            pid = os.getpid()
                            os.kill(pid, signal.SIGTERM)
                            exit_program()

                        # we change the directory using os library
                        elif self.command[0:3] == "cd ":
                            os.chdir(self.command[3:])
                            self.client_socket.send(os.getcwd().encode())

                        # we take screenshot of out window and send to the server
                        elif self.command == 'screenshot':
                            try:
                                # we tell the server to get ready to accept the screenshot image
                                self.client_socket.send("screenshot--*#($)&".encode())
                                # Server sends back a message to confirm it
                                self.client_socket.recv(1024)
                                try:
                                    self.file_name = "screenshot--*#($)&.png"
                                    self.screenshot = pyscreenshot.grab()
                                    self.screenshot.save(self.file_name)

                                    self.file_size = os.path.getsize(self.file_name)
                                
                                    self.client_socket.send(f"{self.file_name}|{self.file_size}".encode())
                                    self.msg = self.client_socket.recv(1024)
                                except:
                                    self.msg = "not ok"
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
                                    self.client_socket.send(self.msg.encode())

                            except:
                                pass

                        # we send the file which server asked
                        elif self.command[0:8] == "showfile":
                            try:
                                self.file_name = self.command[9:]
                                self.file_size = os.path.getsize(self.file_name)
                                send_file = True
                            except:
                                send_file = False
                                self.client_socket.send("not ok".encode())

                            if send_file:
                                self.client_socket.send("showfile--*#($)&".encode())
                                self.client_socket.recv(1024)

                                try:      
                                    self.client_socket.send(f"{self.file_name}|{self.file_size}".encode())
                                    self.msg = self.client_socket.recv(1024)
                                    if self.msg == b'ok':
                                        try:
                                            file = open(self.file_name, 'rb')
                                            data = file.read()
                                        except:
                                            self.client_socket.send("could not open the file!".encode())
                                        try:
                                            self.client_socket.sendall(data)
                                            self.client_socket.recv(1024)
                                        except:
                                            self.client_socket.send("could not send data!".encode())
                                    else:
                                        pass
                                except Exception as e:
                                    print(e)
                                

                                
                        else:
                            try:
                                completed_process = subprocess.run(self.command, shell=True, check=True, timeout=2, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                self.output = completed_process.stdout.decode()
                            except subprocess.TimeoutExpired:
                                self.output = "Command timed out after 2 seconds"
                            except subprocess.CalledProcessError as e:
                                self.output = e.stderr.decode()
                                
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
# The gui window which will be shown in the beggining of the program that the program user can choose: server or client
class Login_frame():
    
    def __init__(self, window):

        self.window = window

        
    def show(self):

        x_offset = (screen_windth - WIDTH) // 2
        y_offset = (screen_height - HEIGHT) // 2

        # i usually use f"" , but just wanted to test the old fashion way!
        root.geometry("{}x{}+{}+{}".format(WIDTH, HEIGHT, x_offset, y_offset))
        
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
                                    width=70,height=2,
                                    command=self.choosen_server
                                    )
        self.client_btn = tk.Button(self.login_frame,
                                    text="CLIENT",
                                    font=(font_name),
                                    bg=button_color,
                                    fg='black',
                                    width=70,height=2,
                                    command=self.choosen_client
                                    )

        self.login_frame.place(x=10, y=10)
        self.login_frame.pack_propagate(False)
        self.login_frame.configure(width=780, height=580, background='white')
        # Appending our content
        self.choose_label.place(x=315, y=210)
        self.server_btn.place(x=30, y=320)
        self.client_btn.place(x=30, y=372)
        

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
# SERVER-GUI
class Server_frame():
    def __init__(self, window):
        
        window_width = 1600
        window_height = 900

        root.geometry(f"{window_width}x{window_height}+{(screen_windth - window_width)//2}+{(screen_height - window_height)//2}")

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
        self.help_btn = tk.Button(self.options_frame,
                                  text='Help',
                                  font=(font_name, 25),
                                  bg=button_color,
                                  padx=20,width=10,height=1,
                                  pady=1,anchor="n",
                                  command=lambda: (self.help_page())
                                  )

        # Showing the Options bar
        self.choose_user_btn.place(x=22, y=50)
        self.connect_btn.place(x=22, y=130)
        self.command_btn.place(x=22, y=210)
        self.help_btn.place(x=22, y=290)


        # --------------------right bar--------------------
        # ----Client-information----
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
    def choose_user_page(self):

        # we stop the threads here
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


    # --------------------Connection-page--------------------
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
        
        # ----------------------------------------Listbox-scrollbar----------------------------------------
        # Command-Line

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

    # ----------Help page----------
    # The Manual of our program
    def help_page(self):
        self.indicate(self.help_btn)
        self.help_page_frame = tk.Frame(self.main_frame)

        self.help_page_frame.place(x=0, y=0)
        self.help_page_frame.pack_propagate(False)
        self.help_page_frame.configure(width=960, height=880)
        
        self.help_list = tk.Listbox(self.help_page_frame,
                                    font=(font_name, 20),
                                    fg='black',
                                    bg='#d9d9d9'
                                    )
        self.help_scrollbar = tk.Scrollbar(self.help_page_frame)

        self.help_scrollbar.pack(side=tk.RIGHT, fill='y')
        self.help_list.pack(side='left', expand=True, fill='both')

        self.help_list.config(yscrollcommand=self.help_scrollbar.set)
        self.help_scrollbar.config(command=self.help_list.yview)

        self.help = """                                                      Manual
PROGRAM USAGE
    -Back
        If you want to change user, you can press the 'Back' button from 
        the left bar.

    -Connection:
        If you have Internet connection, your ip address must be emerged
        in the 'IP Addr' entry.
        For instance it can be '192.168.0.1'.
        Otherwise your local ip address will be showed which is '127.0.0.1'
        You have to also specify a port or you can use a default port whcih
        is '8119'.
        To start listening, you can press the 'START' button.
        After the client connects to to the server(you), the background
        will be green and you will automaticlly be directed  to the 
        'Command Line'.

    -Command Line
        You can type you command and press send.
        You can send any 'windows command line' (cmd) commands to use the
        program.
        For instance, you can send "dir" command to see the content of the
        directory you are.
        Furthermore we have also comtumized more command:
            -screenshot
                This command will take an screenshot of the client's window
                and also save it in the server's computer, in the directory of
                the program file.
            -showfile <file name>
                This command will show the specified file from the client
                computer, and also save it in the server's computer, in the
                directory of the program file.
            -exit
                This command will exit the clients from the program.
    
    -help
        To read the Manual you can visit the help page.
    
AUTHOR
    Original Manage by <author's name> <inf2022001@ionio.gr>
                                                    9 May 2023
        """

        self.help_lines = self.help.split('\n')
        for line in self.help_lines:
            self.help_list.insert(tk.END, line)



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
# CLIENT-GUI
class Client_frame():
    def __init__(self, window):

        x_offset = (screen_windth - WIDTH) // 2
        y_offset = (screen_height - HEIGHT) // 2

        root.geometry("{}x{}+{}+{}".format(WIDTH, HEIGHT, x_offset, y_offset))

        destroy_old_frames(window)

        # Frames
        self.cln_options_frame = tk.Frame(window)
        self.cln_main_frame = tk.Frame(window)
        self.cln_right_frame = tk.Frame(window)

        # Showing the Frames
        self.cln_options_frame.place(x=10, y=10)
        self.cln_options_frame.pack_propagate(False)
        self.cln_options_frame.configure(width=780, height=55)

        self.cln_main_frame.place(x=10, y=75)
        self.cln_main_frame.pack_propagate(False)
        self.cln_main_frame.configure(width=540, height=515)

        self.cln_right_frame.place(x=560, y=75)
        self.cln_right_frame.pack_propagate(False)
        self.cln_right_frame.configure(width=230, height=515)


        # ----------Options-bar(left bar)----------
        self.cln_choose_user_btn = tk.Button(self.cln_options_frame,
                                       text='Back',
                                       font=(font_name, 25),
                                       bg=button_color,
                                       padx=20,pady=1,
                                       width=10,height=1,
                                       anchor="n",
                                       command=lambda: self.cln_choose_user_page()
                                       )
        self.cln_connect_btn = tk.Button(self.cln_options_frame,
                                     text='Connect',
                                     font=(font_name, 25),
                                     bg=button_color,
                                     padx=20,pady=1,
                                     width=10,height=1,
                                     anchor="n",
                                     command=lambda: self.cln_connect_page()
                                     )
        self.cln_help_btn = tk.Button(self.cln_options_frame,
                                  text='Help',
                                  font=(font_name, 25),
                                  bg=button_color,
                                  padx=20,pady=1,
                                  width=10,height=1,
                                  anchor="n",
                                  command=lambda: self.cln_help_page()
                                  )
        
        
        self.cln_choose_user_btn.place(x=5, y=5)
        self.cln_connect_btn.place(x=262, y=5)
        self.cln_help_btn.place(x=520, y=5)


    # --------------------Voice-chat-bar--------------------
        self.voice_chat_label = tk.Label(self.cln_right_frame,
                                         text='Voice Chat',
                                         font=(font_name, 15)
                                         )
        self.voice_chat_label.pack(side='top')

    # --------------------Functions-------------------------
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

        self.help_list = tk.Listbox(self.cln_main_frame,
                                    font=(font_name, 20),
                                    fg='black',
                                    bg='#d9d9d9'
                                    )
        self.help_scrollbar = tk.Scrollbar(self.cln_main_frame)

        self.help_scrollbar.pack(side=tk.RIGHT, fill='y')
        self.help_list.pack(side='left', expand=True, fill='both')

        self.help_list.config(yscrollcommand=self.help_scrollbar.set)
        self.help_scrollbar.config(command=self.help_list.yview)

        self.help = """                           Manual
PROGRAM USAGE
    To use the program, you need to
    connect to a server.
    In the connect page, you can see
    'SERVER IP' and 'port'.
    You have to insert the server's
    information there, you can ask 
    the server to get his information.
    After you insert the server's data
    and you press the 'START' button,
    you are trying to connect the server.
    After the connection the background 
    will turn to green and the server 
    can sends commands to your 
    computer.

    If you want to change user, you can
    easly press the 'BACK' and choose
    'server'.

    To read the Manual you can visit the
    help page.
    
AUTHOR
    Original Manage by <author's name>
    <inf2022001@ionio.gr>
                        9 May 2023
        """

        self.help_lines = self.help.split('\n')
        for line in self.help_lines:
            self.help_list.insert(tk.END, line)

# ____________________Functions____________________

# Each time we change pages, we destroy the old page(frames), and append the conntend to the new page(frame)
def destroy_old_frames(frame):
    for children_frame in frame.winfo_children():
        children_frame.destroy()


# This function return the users private ip address
def get_private_ip_address():
    try:
        # If it is connected to Internet, the function returns the private ip address
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # '8.8.8.8' it is for google and it is always running
        temp_socket.connect(('8.8.8.8', 80))
        ip_address = temp_socket.getsockname()[0]
        # otherwise return the local ip
    except socket.error:
        ip_address = '127.0.0.1'
    finally:
        temp_socket.close()
    return ip_address


# Fuctions that check if an ip address is valid
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


# Functions that check if a port number is valid
def is_valid_port(port):
    try:
        port = int(port)
        if 1024 < port and port < 65535:
            return True
        else:
            return False
    except ValueError:
        return False


# Exits the program, stopping the threads before
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


# If users press the x-button(on the top right), we first ask, and then close the program
def x():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        exit_program()

#__________________________________________________


# Creating a window
root = tk.Tk()

screen_windth = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

WIDTH = 800
HEIGHT = 600

x_offset = (screen_windth - WIDTH) // 2
y_offset = (screen_height - HEIGHT) // 2

root.geometry("{}x{}+{}+{}".format(WIDTH, HEIGHT, x_offset, y_offset))

root.configure(background='red')
root.title("Ionio university of Kerkyra")
root.protocol("WM_DELETE_WINDOW", x)


# Runnig program 
run_login = Login_frame(root)
run_login.show()


root.mainloop()
