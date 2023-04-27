import tkinter as tk
import socket
import threading
from getpass import getuser
from platform import uname
from time import sleep
import subprocess
import os

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

        # This is the voice chat socket
        self.voice_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # All the threads
        self.recv_out_put_thread = threading.Thread(target=self.recv_out_put, args=())

        # We stop the threads using boolean variables, indeed we break the loop of the function  
        self.recv_out_put_bool = True

        self.is_client_connected = False
        self.is_server_listening = False
        self.server_listen_acccept_bool = True

    # This function checks if we can start a server on given ip address and port, if yes we start listening
    def server_listen_accept(self, ip_addr, port):
        try:
            self.server_socket.bind((ip_addr, int(port)))
            self.server_socket.listen(1)
            run_login.run_server.listen_btn.config(state='disabled')
            run_login.run_server.print_server_connection_state.config(text='Listening...')
            if run_login.run_server.socket_error.winfo_exists():
                run_login.run_server.socket_error.destroy()
            self.is_server_listening = True

            while self.server_listen_acccept_bool:
                try:
                    self.client, self.addr = self.server_socket.accept()
                    run_login.run_server.addr_0_label.config(text=self.addr[0])
                    run_login.run_server.addr_1_label.config(text=self.addr[1])
                    
                    # After the connection, first we receive the client username
                    self.client_username = self.client.recv(1024).decode()
                    run_login.run_server.right_bar_client_label.config(text=self.client_username)

                    self.server_listen_accept_bool = False
                    self.is_server_listening = False
                    self.is_client_connected = True 

                    # After the connection, the user page will be chaged automaticlly to command Line page
                    run_login.run_server.command_page()
                    self.recv_out_put_thread.start()

                    # After connection, we change the background color from "red" to "green"
                    root.configure(background='green')
                except:
                    self.server_socket.close()
                    print("failed , server_listen_accept, while True, except ERROR")
                    sleep(3)
                    break

        # If we can't creat server and start listening, we show to the user the reason(error)
        except socket.error as error:
            if str(error) == "[Errno 98] Address already in use":
                run_login.run_server.print_server_connection_state.config(text="Use an other port and Try again!")

            run_login.run_server.socket_error.pack()
            run_login.run_server.socket_error.config(text=error)


        


        
        
    # Whith this fuction we send our command to the client
    def send_command(self):
        self.cmnd = run_login.run_server.command_entry.get()
        run_login.run_server.command_entry.delete(0, tk.END)
        if self.is_client_connected :
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
            print("client is NOT connected!")
        

    def recv_out_put(self):
        while self.is_client_connected and self.recv_out_put_bool:
            self.output = self.client.recv(1024).decode()
            run_login.run_server.output_list.append(self.output)
            destroy_old_frames(run_login.run_server.inner_frame)
            run_login.run_server.print_output()
            

    def voice_socket():
        pass








# ____________________client-socket____________________
class Client():

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.get_send_command_thread = threading.Thread(target=self.get_send_command, args=())

        self.client_windows_username = getuser()

        self.is_client_connecting = False
        self.is_connected_to_server = False
        self.stop_get_send_command_loop = True


    def client_connect(self, ip_addr, port):
        self.is_client_connecting = True

        while not self.is_connected_to_server:
            try:
                self.client_socket.connect((str(ip_addr), int(port)))
                
                self.is_connected_to_server = True
            except socket.error as error:
                if str(error) == "[Errno 111] Connection refused":
                    try:
                        run_login.run_client.print_connection_state_label.config(text='Connecting')
                        sleep(1)
                        run_login.run_client.print_connection_state_label.config(text='Connecting.')
                        sleep(1)
                        run_login.run_client.print_connection_state_label.config(text="Connecting..")
                        sleep(1)
                        run_login.run_client.print_connection_state_label.config(text="Connecting...")
                        sleep(1)
                    except:
                        sleep(1)
                else:
                    run_login.run_client.print_connection_state_label.config(text=error)

        self.client_socket.send(self.client_windows_username.encode())
        self.get_send_command_thread.start()

        run_login.run_client.client_connect_server.config(state='disabled')
        root.configure(background='green')

        self.is_client_connecting = False
                

    def get_send_command(self):
        while self.stop_get_send_command_loop:
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




# ____________________login-window____________________
class Login_frame():
    
    def __init__(self, window):

        destroy_old_frames(window)
        
        # The Frame
        self.login_frame = tk.Frame(window)

        self.login_frame.place(x=10, y=10)
        self.login_frame.pack_propagate(False)
        self.login_frame.configure(width=1580, height=880, background='white')
        
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


        # ----------Notification----------
        self.right_bar_notification_frame = tk.Frame(self.right_frame)

        self.right_bar_notification_frame.place(x=5, y=290)
        self.right_bar_notification_frame.pack_propagate(False)
        self.right_bar_notification_frame.configure(width=290, height=300)

        self.right_bar_notification_label = tk.Label(self.right_bar_notification_frame,
                                                     font=(font_name, 15),
                                                     text='Notifications',
                                                     padx=0, pady=10
                                                     )
        self.right_bar_notification_label.pack(side='top')

        self.right_bar_notification_inner_frame = tk.Frame(self.right_bar_notification_frame)
        self.right_bar_notification_inner_frame.pack()
        
        self.right_bar_notification_msg = tk.Text(self.right_bar_notification_inner_frame,
                                                  font=(font_name),
                                                  width=27, height=13,
                                                  background='#e6e6e6'
                                                  )
        self.right_bar_notification_scrollbar = tk.Scrollbar(self.right_bar_notification_inner_frame,
                                                             orient='vertical',
                                                             command=self.right_bar_notification_msg.yview
                                                             )
        self.right_bar_notification_msg.configure(yscrollcommand=self.right_bar_notification_scrollbar.set)
        self.right_bar_notification_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    
        self.right_bar_notification_msg.insert('end', 'hello world this is john smith and i am learning python')
        self.right_bar_notification_msg.pack(side=tk.LEFT, fill='both', expand=True)


        # ----------voice chat----------
        self.right_bar_voice_frame = tk.Frame(self.right_frame)

        self.right_bar_voice_frame.place(x=5, y=595)
        self.right_bar_voice_frame.pack_propagate(False)
        self.right_bar_voice_frame.configure(width=290, height=280)

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
        if run_login.server is None:
            pass
        else:
            del run_login.server
        if run_login.run_server is None:
            pass
        else:
            del run_login.run_server
        
        run_login



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
        self.out_put_frame = tk.Frame(self.main_frame)

        self.output_label = tk.Label(self.main_frame,
                                     text="Output:",
                                     font=(font_name, 15)
                                     )
        self.output_label.place(x=50, y=20)
        
        # ----------------------------------------scrollbar canvas----------------------------------------
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
        # --------------------------------------------------------------------------------------------------

        self.print_new_command_label = tk.Label(self.main_frame,
                                                text='New Command:',
                                                font=(font_name, 15)
                                                )
        self.command_entry = tk.Entry(self.main_frame,
                                      font=(font_name, 20),
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
            self.listening_thread = threading.Thread(target=run_login.server.server_listen_accept, args=(self.server_ip, self.server_port))
            self.listening_thread.start()


    def print_output(self):
        for i in self.output_list:
            self.print_output_label = tk.Label(self.inner_frame,
                                        text=i,
                                        font=(font_name, 20),
                                        fg='green',
                                        bg='black',
                                        anchor='nw',
                                        justify='left'
                                        )
            self.print_output_label.pack(fill='both', expand=True)






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
        Login_frame(root)

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
    root.destroy()
    exit()

#__________________________________________________


# Creating a window
root = tk.Tk()
root.geometry("1600x900")
root.configure(background='red')
root.title("Matin")

# Runnig program 
run_login = Login_frame(root)


root.mainloop()
