"""GUI"""

import tkinter as tk

HEIGHT = 720
WIDTH = 1280
RL_HEIGHT = 600
RL_WIDTH = 600

FONT = 40
GRAY = '#E3E2E2'

SPACING_X = 0.04
SPACING_Y = 0.12


class GUI:
    """A class representing the GUI"""
    # Private Instance Attributes:
    #   - _root:
    root = tk.Tk()

    def display_register_window(self) -> None:
        """Register window to let users register"""
        register_root = tk.Toplevel(self.root)
        register_root.title('Register')
        register_root.geometry('600x600')

        label = tk.Label(register_root, text='Please enter the required information below')
        label.pack(pady=20)
        username_label = tk.Label(register_root, text='Username:')
        username_label.pack(pady=10)

        username_entry = tk.Entry(register_root, font=FONT)
        username_entry.pack()

        password_label = tk.Label(register_root, text='Password:')
        password_label.pack(pady=10)

        password_entry = tk.Entry(register_root, font=FONT)
        password_entry.pack(pady=10)

        displayed_word = tk.StringVar(self.root)
        displayed_word.set('Gender')

        gender_dropdown = tk.OptionMenu(register_root, displayed_word, 'Male', 'Female', 'Other')
        gender_dropdown.pack(pady=20)

        birth_label = tk.Label(register_root, text='Date of Birth (month, day, year):')
        birth_label.pack(pady=20)

        word_month = tk.StringVar(self.root)
        word_month.set('Month')

        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
                  'Sept', 'Oct', 'Nov', 'Dec']
        month_dropdown = tk.OptionMenu(register_root, word_month, *months)
        month_dropdown.place(relx=0.3, rely=0.55)

        word_year = tk.StringVar(self.root)
        word_year.set('Year')

        year = [str(y) for y in range(2021, 1920, -1)]
        year_dropdown = tk.OptionMenu(register_root, word_year, *year)
        year_dropdown.place(relx=0.57, rely=0.55)

        word_day = tk.StringVar(self.root)
        word_day.set('Day')

        day = [str(x) for x in range(1, 32)]
        day_dropdown = tk.OptionMenu(register_root, word_day, *day)
        day_dropdown.place(relx=0.45, rely=0.55)

        space = tk.Label(register_root)
        space.pack(pady=20)

        register_button = tk.Button(register_root, text='Register', font=FONT)
        register_button.pack(pady=20)

    def display_login_window(self) -> None:
        """Login window to let users login"""

        login_root = tk.Toplevel(self.root)
        login_root.title('Login')
        login_root.geometry('600x600')

        username_label = tk.Label(login_root, text='Username:')
        username_label.pack(pady=10)

        username_entry = tk.Entry(login_root, font=FONT)
        username_entry.pack()

        password_label = tk.Label(login_root, text='Password:')
        password_label.pack(pady=10)

        password_entry = tk.Entry(login_root, font=FONT)
        password_entry.pack(pady=10)

        register_button = tk.Button(login_root, text='Login', font=FONT)
        register_button.pack(pady=20)

    def initialize_components(self) -> None:
        """Initialize the components for GUI"""

        self.root.title('AnimeList')

        window = tk.Canvas(self.root, height=HEIGHT, width=WIDTH)
        window.pack()

        background_image = tk.PhotoImage(file='anime_wallpaper.png')
        background_label = tk.Label(self.root, image=background_image)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        frame = tk.Frame(self.root, bg=GRAY)
        frame.place(relx=SPACING_X, rely=SPACING_Y, relheight=0.1, relwidth=0.625)

        search_bar = tk.Entry(frame, font=FONT, textvariable='Search')
        search_bar.place(relx=0.025, rely=0.25, relheight=0.5, relwidth=0.75)

        search_button = tk.Button(frame, text='Search Anime', font=FONT)
        search_button.place(relx=0.8, rely=0.25, relheight=0.5, relwidth=0.2)

        frame_rb = tk.Frame(self.root, bg=GRAY)
        frame_rb.place(relx=SPACING_X, rely=0.25, relheight=0.7, relwidth=0.625)

        recommendation_box = tk.Label(frame_rb)
        recommendation_box.place(relx=0.025, rely=0.035, relheight=0.93, relwidth=0.95)

        displayed_word = tk.StringVar(self.root)
        displayed_word.set('Genre')

        dropdown_frame = tk.Frame(self.root, bg='#E3E2E2')
        dropdown_frame.place(relx=0.75, rely=SPACING_Y + 0.025, relheight=0.06, relwidth=0.08)

        genre_dropdown = tk.OptionMenu(dropdown_frame, displayed_word, 'Action', 'Adventure')
        genre_dropdown.place(relheight=1.0, relwidth=1.0)

        login_frame = tk.Frame(self.root, bg=GRAY)
        login_frame.place(relx=0.88, rely=0.01, relheight=0.05, relwidth=0.05)
        login_button = tk.Button(login_frame, text='Login', command=self.display_login_window,
                                 font=FONT)
        login_button.place(relheight=1.0, relwidth=1.0)

        register_frame = tk.Frame(self.root, bg=GRAY)
        register_frame.place(relx=0.94, rely=0.01, relheight=0.05, relwidth=0.05)
        register_button = tk.Button(register_frame, text='Register',
                                    command=self.display_register_window, font=FONT-10)
        register_button.place(relheight=1.0, relwidth=1.0)

        self.root.mainloop()


gui = GUI()
gui.initialize_components()
