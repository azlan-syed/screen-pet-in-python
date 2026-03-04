import tkinter as tk
import time
import random
import math

class DesktopPet:
    def __init__(self):
        self.root = tk.Tk()
        
        # Window settings
        self.w = 150
        self.h = 150
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.bg_color = '#ABCDEF'
        self.root.attributes('-transparentcolor', self.bg_color)
        self.root.config(bg=self.bg_color)
        
        # Center initially
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.x = sw // 2
        self.y = sh // 2
        self.root.geometry(f'{self.w}x{self.h}+{self.x}+{self.y}')
        
        self.canvas = tk.Canvas(self.root, width=self.w, height=self.h, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack()
        
        # Pet Properties
        self.body_color = 'SkyBlue1'
        self.state = 'IDLE' # IDLE, WALK, FOLLOW, DRAG
        self.eyes_crossed = False
        self.tongue_out = False
        self.wink = False
        
        # Movement
        self.target_x = self.x
        self.target_y = self.y
        self.speed = 2
        
        # Dragging support
        self.offset_x = 0
        self.offset_y = 0
        
        self.setup_pet()
        self.bind_events()
        
        self.update_loop()
        self.blink_loop()
        self.wander_loop()
        
    def setup_pet(self):
        c = self.canvas
        # Scale factor (original was 400, new is 150)
        s = 150/400
        
        # Helper to scale coordinates
        def sc(coords):
            return [x * s for x in coords]

        self.body = c.create_oval(sc([35, 20, 365, 350]), outline=self.body_color, fill=self.body_color)
        self.ear_left = c.create_polygon(sc([75, 80, 75, 10, 165, 70]), outline=self.body_color, fill=self.body_color)
        self.ear_right = c.create_polygon(sc([255, 45, 325, 10, 320, 70]), outline=self.body_color, fill=self.body_color)
        self.foot_left = c.create_oval(sc([65, 320, 145, 360]), outline=self.body_color, fill=self.body_color)
        self.foot_right = c.create_oval(sc([250, 320, 330, 360]), outline=self.body_color, fill=self.body_color)
        
        self.eye_left = c.create_oval(sc([130, 110, 160, 170]), outline='black', fill='white')
        self.pupil_left = c.create_oval(sc([140, 145, 150, 155]), outline='black', fill='black')
        
        self.eye_right = c.create_oval(sc([230, 110, 260, 170]), outline='black', fill='white')
        self.pupil_right = c.create_oval(sc([240, 145, 250, 155]), outline='black', fill='black')
        
        self.mouth_normal = c.create_line(sc([170, 250, 200, 272, 230, 250]), smooth=1, width=2, state=tk.NORMAL)
        self.mouth_happy = c.create_line(sc([170, 250, 200, 282, 230, 250]), smooth=1, width=2, state=tk.HIDDEN)
        
        self.tongue_main = c.create_rectangle(sc([170, 250, 230, 290]), outline='red', fill='red', state=tk.HIDDEN)
        self.tongue_tip = c.create_oval(sc([170, 285, 230, 300]), outline='red', fill='red', state=tk.HIDDEN)
        
        self.cheek_left = c.create_oval(sc([70, 180, 120, 230]), outline='pink', fill='pink', state=tk.HIDDEN)
        self.cheek_right = c.create_oval(sc([280, 180, 330, 230]), outline='pink', fill='pink', state=tk.HIDDEN)

    def bind_events(self):
        self.root.bind('<Button-1>', self.start_drag)
        self.root.bind('<B1-Motion>', self.drag)
        self.root.bind('<ButtonRelease-1>', self.stop_drag)
        self.root.bind('<Double-1>', self.toggle_follow)
        self.root.bind('<Button-3>', self.show_menu)
        self.root.bind('<Enter>', self.show_happy)
        self.root.bind('<Leave>', self.hide_happy)
        
    def start_drag(self, event):
        self.state = 'DRAG'
        self.offset_x = event.x
        self.offset_y = event.y
        self.show_happy(None)

    def drag(self, event):
        if self.state == 'DRAG':
            self.x = self.root.winfo_pointerx() - self.offset_x
            self.y = self.root.winfo_pointery() - self.offset_y
            self.root.geometry(f'+{self.x}+{self.y}')

    def stop_drag(self, event):
        self.state = 'IDLE'
        self.hide_happy(None)

    def toggle_follow(self, event):
        if self.state == 'FOLLOW':
            self.state = 'IDLE'
        else:
            self.state = 'FOLLOW'

    def show_happy(self, event):
        self.canvas.itemconfigure(self.cheek_left, state=tk.NORMAL)
        self.canvas.itemconfigure(self.cheek_right, state=tk.NORMAL)
        self.canvas.itemconfigure(self.mouth_happy, state=tk.NORMAL)
        self.canvas.itemconfigure(self.mouth_normal, state=tk.HIDDEN)

    def hide_happy(self, event):
        if self.state != 'DRAG':
            self.canvas.itemconfigure(self.cheek_left, state=tk.HIDDEN)
            self.canvas.itemconfigure(self.cheek_right, state=tk.HIDDEN)
            self.canvas.itemconfigure(self.mouth_happy, state=tk.HIDDEN)
            self.canvas.itemconfigure(self.mouth_normal, state=tk.NORMAL)

    def show_menu(self, event):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="State: " + self.state, state=tk.DISABLED)
        menu.add_command(label="Toggle Follow", command=lambda: self.toggle_follow(None))
        menu.add_separator()
        menu.add_command(label="Exit", command=self.root.destroy)
        menu.post(event.x_root, event.y_root)

    def update_loop(self):
        if self.state == 'FOLLOW':
            mx = self.root.winfo_pointerx() - self.w // 2
            my = self.root.winfo_pointery() - self.h // 2
            self.move_towards(mx, my)
        elif self.state == 'WALK':
            self.move_towards(self.target_x, self.target_y)
            if abs(self.x - self.target_x) < 5 and abs(self.y - self.target_y) < 5:
                self.state = 'IDLE'
        
        # Physics/Animation
        now = time.time()
        hop = 0
        if self.state in ['FOLLOW', 'WALK']:
            # Create a hopping effect (absolute sine wave for a bounce)
            hop = abs(math.sin(now * 10)) * 20
        
        # Apply position
        self.root.geometry(f'+{int(self.x)}+{int(self.y - hop)}')
            
        self.root.after(20, self.update_loop)

    def move_towards(self, tx, ty):
        dx = tx - self.x
        dy = ty - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist > self.speed:
            # Face the direction? (Maybe later)
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed
        else:
            self.x = tx
            self.y = ty

    def blink_loop(self):
        # Eyes
        self.canvas.itemconfigure(self.eye_left, fill=self.bg_color)
        self.canvas.itemconfigure(self.eye_right, fill=self.bg_color)
        self.canvas.itemconfigure(self.pupil_left, state=tk.HIDDEN)
        self.canvas.itemconfigure(self.pupil_right, state=tk.HIDDEN)
        
        self.root.after(200, self.open_eyes)
        self.root.after(random.randint(3000, 6000), self.blink_loop)

    def open_eyes(self):
        self.canvas.itemconfigure(self.eye_left, fill='white')
        self.canvas.itemconfigure(self.eye_right, fill='white')
        self.canvas.itemconfigure(self.pupil_left, state=tk.NORMAL)
        self.canvas.itemconfigure(self.pupil_right, state=tk.NORMAL)

    def wander_loop(self):
        if self.state == 'IDLE' and random.random() < 0.3:
            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            self.target_x = random.randint(0, sw - self.w)
            self.target_y = random.randint(0, sh - self.h)
            self.state = 'WALK'
        
        self.root.after(5000, self.wander_loop)

if __name__ == "__main__":
    pet = DesktopPet()
    pet.root.mainloop()
