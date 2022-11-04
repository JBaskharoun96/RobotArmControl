import PySimpleGUI as sg
import math


class JoyStick:
    
    def __init__(self, r_max=150, stick_size=40):
        down=True
        ExtendDown=True
        GrabDown=True
        self.down=down
        self.ExtendDown = ExtendDown
        self.GrabDown = GrabDown
        self.r_max = r_max
        self.stick_size = stick_size
        size = int(self.stick_size / 2)
        layout = [
            [sg.Graph(canvas_size=(2 * self.r_max, 2 * self.r_max),
                      graph_bottom_left=(0, 0),
                      graph_top_right=(2 * self.r_max, 2 * self.r_max),
                      change_submits=True,
                      drag_submits=True,
                      key='graph'),sg.Text('', size=(20,1)),
                      sg.Button('Extend Arm', size=(10,1), button_color='white on green', key='-C-'),sg.Button('Grab', size=(6,1), button_color='white on green', key='-D-')],
            [sg.Text('X-Z Coordinates: (0, 0)        ', key='-xz-'), ],  # I put spaces to secure space,
            #[sg.Button('On', size=(3, 1), button_color='white on green', key='-B-')],
            [sg.Text('', size=(20,1))],
            [sg.Text('', size=(50,1)), sg.Button('Exit', size=(4,2))]
            
        ]
        window = sg.Window('Control Panel', layout, finalize=True, size=(800,450))
        self.__window = window
        self.__graph = window['graph']
        cir = self.__graph.DrawOval((0, 0), (2 * self.r_max, 2 * self.r_max))
        self.__graph.DrawOval((int(self.r_max / 2), int(self.r_max / 2)),
                              (int(self.r_max * 3 / 2), int(self.r_max * 3 / 2)))
        self.__graph.DrawLine((0, self.r_max), (self.r_max * 2, self.r_max))
        self.__graph.DrawLine((self.r_max, 0), (self.r_max, self.r_max * 2))
        self.__cir_joy = self.__graph.DrawOval((self.r_max - size, self.r_max - size),
                                               (self.r_max + size, self.r_max + size))
        self.__cir_joy_pos = (self.r_max, self.r_max)
        self.__graph.TKCanvas.itemconfig(cir, fill="white")
        self.__graph.TKCanvas.itemconfig(self.__cir_joy, fill="cyan")
        self.close = False
        self.xz_coordinates = [0, 0]
        self.rt_coordinates = [0, 0]
        self.z_coordinate=[0]

    def __joy_pos_setter(self, x_togo, y_togo):
        posx, posy = self.__cir_joy_pos

        if math.sqrt((x_togo-self.r_max)**2 + (y_togo-self.r_max)**2) < self.r_max - self.stick_size/2:
            dx = x_togo - posx
            dy = y_togo - posy
            self.__graph.MoveFigure(self.__cir_joy, dx, dy)
            self.__cir_joy_pos = (x_togo, y_togo)
        

    def __show_coordinates(self, position):
        self.xz_coordinates = int(self.__cir_joy_pos[0]) - self.r_max, int(self.__cir_joy_pos[1]) - self.r_max
        

    def run(self):
        while True:
            self.update()
            if self.close:
                break
    
    def update(self):
        
        event, values = self.__window.read(timeout=100)
        if event == "Exit" or event == sg.WIN_CLOSED:
            self.close = True
        elif event == 'graph+UP':
            self.__joy_pos_setter(self.r_max, self.r_max)
            self.__show_coordinates((self.r_max, self.r_max))
            self.__window['-xz-'].update(f'X-Z Coordinates: (0, 0)')
        elif event == '-B-':                # if the normal button that changes color and text
            self.down = not self.down
            self.__window['-B-'].update(text='On' if self.down else 'Off', button_color='white on green' if self.down else 'white on red')
           # self.close = False 
           
        elif event == '-C-':                # if the normal button that changes color and text
            self.ExtendDown = not self.ExtendDown
            self.__window['-C-'].update(text='Extend Arm' if self.ExtendDown else 'Retract Arm', button_color='white on green' if self.ExtendDown else 'white on red')
           # self.close = False
           
        elif event == '-D-':                # if the normal button that changes color and text
            self.GrabDown = not self.GrabDown
            self.__window['-D-'].update(text='Grab' if self.GrabDown else 'Release', button_color='white on green' if self.GrabDown else 'white on red')
           # self.close = False 

        elif event == 'graph':
            position = values['graph']
            self.__joy_pos_setter(position[0], position[1])
            self.__show_coordinates(position)
            text1 = f'X-Z Coordinates: ' \
                    f'({self.xz_coordinates[0]}, {self.xz_coordinates[1]})'

            self.__window['-xz-'].update(text1)


    def closeWindow(self):
        self.close = True
        self.__window.close()


if __name__ == '__main__':
    js = JoyStick()
    js.run()

