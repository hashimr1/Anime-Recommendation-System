"""CSC111 Final Project: My Anime Recommendations
==================================================================
The Application class

This module contains the class definition for the main application
using tkinter.
==================================================================
@authors: Tahseen Rana, Tu Pham
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
from recommendation_engine import RecommendationEngine
from data_loader import create_anime_graph_from_data
from anime_graph import Anime
import threading
##########################################################################
# ==========  The default dimensions of GUI components  ================ #
##########################################################################

# The dimensions of the main window
HEIGHT = '720'
WIDTH = '1280'
WINDOW_DIM = WIDTH + 'x' + HEIGHT

# The dimensions of the register window
RW_HEIGHT = '600'
RW_WIDTH = '600'
RW_DIM = RW_WIDTH + 'x' + RW_HEIGHT

# Default margins for widgets near the window border.
# This also applies to bottom and right symmetrically
TOP_MARGIN = 0.022
LEFT_MARGIN = 0.015

# The default dimensions of buttons in relation to the main window.
BUTTON_WIDTH = 0.06
BUTTON_HEIGHT = 0.05
BUTTON_BORDER_W = 1

# Dimensions of an anime-info frame in relation to the main content-canvas
ANI_FRAME_W = 0.2
ANI_FRAME_H = 0.3

# Predefined colors
FONT = 40
GRAY = '#E3E2E2'
RED = '#FF2D00'

# ======================================================================= #
###########################################################################


class Application(tk.Tk):
    """A class representing the GUI."""
    # The GUI components necessary for input/output
    background_image: tk.PhotoImage
    anime_covers: list[tk.PhotoImage]
    content_frame: tk.Frame

    # String variable associated with the search bar
    query: tk.StringVar

    # Widgets for the login window & register window
    # we need to define them here to get their values on button click.
    username_entry: ttk.Entry
    gender_var: tk.StringVar
    birth_date_var: tk.StringVar
    birth_month_var: tk.StringVar
    birth_year_var: tk.StringVar

    # Class instances for data processing
    # trie: Trie
    recommender: RecommendationEngine

    # The data file paths
    anime_file: str
    profiles_file: str
    reviews_file: str

    def __init__(self, anime_filepath: str, profiles_filepath: str, reviews_filepath: str) -> None:
        """Initialize the Application.
        """
        super().__init__()
        # Initializing components for the recommendation system
        self.anime_file = anime_filepath
        self.profiles_file = profiles_filepath
        self.reviews_file = reviews_filepath

        # Initializing the recommendation engine
        graph = create_anime_graph_from_data(self.anime_file, self.profiles_file,
                                             self.reviews_file)
        self.recommender = RecommendationEngine(graph)

        # Initializing the GUI
        self.title('AnimeList')
        self.geometry(WIDTH + 'x' + HEIGHT)

        # Setting the style
        self.style = ttk.Style(self)
        self.tk.call('source', 'tk_theme/azure.tcl')
        self.style.theme_use('azure')

        # Load the background image for later use
        self.background_image = tk.PhotoImage(file='anime_wallpaper.png')

    def run(self) -> None:
        """Run the app."""
        self._display_login_window()
        self.mainloop()

    def search_for_anime(self, *args) -> None:
        """Display a list of anime names that matches self.query, or partially match the text
        in the search bar."""
        keywords = self.query.get()
        pass

    def _initialize_main_page(self) -> None:
        """Initialize the components for GUI"""
        # The background
        background_label = tk.Label(self, image=self.background_image)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Setting up the search bar
        self.query = tk.StringVar()
        self.query.trace_add('write', self.search_for_anime)
        search_bar = ttk.Entry(self, textvariable=self.query)
        search_bar.place(relx=LEFT_MARGIN, rely=TOP_MARGIN, relheight=0.04, relwidth=0.7)

        # Initializing the content frame
        self.content_frame = self._initialize_content_box()

        # The genre dropdown
        displayed_word = tk.StringVar(self)
        genre_dropdown = ttk.OptionMenu(self, displayed_word, 'Action', 'Adventure')
        genre_dropdown.place(relx=0.725, rely=TOP_MARGIN)
        displayed_word.set('Genre')

        # The logout button
        logout_button = ttk.Button(self, text='Logout', command=self._logout)
        logout_button.place(relx=0.925, rely=TOP_MARGIN)

    def _initialize_content_box(self) -> tk.Frame:
        """Initialize the box containing the main content that is to be shown to the user,
        including recommendations, search results...
        This function returns the frame of the content box.
        """
        outer_frame = tk.Frame(self)
        outer_frame.place(relx=LEFT_MARGIN, rely=TOP_MARGIN + 0.06,
                          relheight=1.0 - TOP_MARGIN * 2 - 0.065,
                          relwidth=1.0 - LEFT_MARGIN * 2)

        self.content_canvas = tk.Canvas(outer_frame)
        self.content_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        # Set up the vertical scrollbar
        vbar = ttk.Scrollbar(outer_frame, orient=tk.VERTICAL,
                             command=self.content_canvas.yview)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.content_canvas.configure(yscrollcommand=vbar.set)

        inner_frame = tk.Frame(self.content_canvas)
        inner_frame.bind('<Configure>', lambda _: self.content_canvas.configure(
                            scrollregion=self.content_canvas.bbox('all')))

        self.content_canvas.create_window((0, 0), window=inner_frame, anchor=tk.NW)

        def _on_mouse_wheel(event) -> None:
            """The callback for the scrollbar."""
            self.content_canvas.yview_scroll(-1 * int((event.delta / 120)), "units")

        self.content_canvas.bind_all("<MouseWheel>", _on_mouse_wheel)

        return inner_frame

    def display_anime_list(self, anime_list: list[Anime]) -> None:
        """display a list of anime recommendations on the canvas.
        Preconditions:
            - self.content_frame is initialized.
        """
        # Clearing the content frame.
        self._clear_main_canvas()
        self.content_canvas.update_idletasks()
        # starts displaying the anime in the list
        for i in range(len(anime_list)):
            col = i % 5
            row = i // 5
            anime = anime_list[i]
            im = Image.open(requests.get(anime.image_url,
                                         stream=True).raw)
            im = im.resize((224, 350), Image.ANTIALIAS)
            self.anime_covers.append(ImageTk.PhotoImage(im))

            button = tk.Button(self.content_frame, text=anime.title,
                               image=self.anime_covers[i],
                               compound='top', width=226, height=380)
            button.grid(row=row, column=col, padx=4, pady=4)

    def _display_register_window(self) -> None:
        """Create a register window for registering."""

        for widget in self.winfo_children():
            widget.destroy()
        # The background
        background_label = tk.Label(self, image=self.background_image)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # The master frame of all register widgets.
        register_frame = ttk.Frame(self)
        register_frame.place(relx=0.5, rely=0.5, relwidth=0.16, relheight=0.54, anchor=tk.CENTER)

        # Username
        username_label = ttk.Label(register_frame, text='Username:')
        username_label.pack(pady=10)
        self.username_entry = ttk.Entry(register_frame)
        self.username_entry.pack(pady=10)

        # password
        password_label = ttk.Label(register_frame, text='Password:')
        password_label.pack(pady=10)
        password_entry = ttk.Entry(register_frame)
        password_entry.pack(pady=10)

        # The gender dropdown
        gender_frame = ttk.Frame(register_frame)
        gender_frame.pack(pady=10)
        gender_label = ttk.Label(gender_frame, text='Gender:')
        gender_label.pack(side='left', padx=10)
        self.gender_var = tk.StringVar()   # The variable for the option
        gender_dropdown = ttk.OptionMenu(gender_frame, self.gender_var, 'Male', 'Female', 'Other')
        gender_dropdown.pack(side='left')

        # The date of birth section
        date_birth_frame = ttk.Frame(register_frame)
        date_birth_frame.pack()
        birth_label = ttk.Label(date_birth_frame, text='Date of Birth (month, day, year):')
        birth_label.pack(pady=10)
        # Month
        self.birth_month_var = tk.StringVar()
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
                  'Sept', 'Oct', 'Nov', 'Dec']
        month_dropdown = ttk.OptionMenu(date_birth_frame, self.birth_month_var, *months)
        month_dropdown.pack(side=tk.LEFT)

        # Day
        self.birth_date_var = tk.StringVar()
        day = [str(x) for x in range(1, 32)]
        day_dropdown = ttk.OptionMenu(date_birth_frame, self.birth_date_var, *day)
        day_dropdown.pack(side=tk.LEFT, padx=10)

        # Year
        self.birth_year_var = tk.StringVar()
        year = [str(y) for y in range(2021, 1920, -1)]
        year_dropdown = ttk.OptionMenu(date_birth_frame, self.birth_year_var, *year)
        year_dropdown.pack(side=tk.RIGHT)

        # The buttons (back/register)
        button_frame = tk.Frame(register_frame)
        button_frame.pack(pady=20)
        back_button = ttk.Button(button_frame, text='Back',
                                 command=self._display_login_window)
        back_button.pack(side=tk.LEFT, padx=6)
        register_button = ttk.Button(button_frame, text='Register',
                                     command=self._register_new_user)
        register_button.pack(side=tk.LEFT, padx=6)

    def _display_login_window(self) -> None:
        """Login window to let users login."""
        for widget in self.winfo_children():
            widget.destroy()

        background_label = tk.Label(self, image=self.background_image)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        login_frame = ttk.Frame(self)
        login_frame.place(relx=0.5, rely=0.5, relwidth=0.16, relheight=0.36, anchor=tk.CENTER)

        username_label = ttk.Label(login_frame, text='Username:')
        username_label.pack(pady=10)
        self.username_entry = ttk.Entry(login_frame)
        self.username_entry.pack(pady=10)

        password_label = ttk.Label(login_frame, text='Password:')
        password_label.pack(pady=10)
        password_entry = ttk.Entry(login_frame)
        password_entry.pack(pady=10)

        # Aligning the buttons
        button_frame = ttk.Frame(login_frame)
        button_frame.pack(pady=20, padx=10)
        login_button = ttk.Button(button_frame, text='Login', command=self._login)
        login_button.pack(side=tk.LEFT, padx=5)

        register_button = ttk.Button(button_frame, text='Register',
                                     command=self._display_register_window)
        register_button.pack(side=tk.LEFT, padx=5)

    def _login(self) -> None:
        """This function is associated with the log in button in the login window.
        It attempts to log a user in the system.
        If the attempt is unsuccessful, an error message box is displayed.
        """
        username = self.username_entry.get()
        if not self.recommender.log_in(username):
            tk.messagebox.showerror("Login unsuccessful",
                                    "The username does not exist. Please try again.")
        else:
            self._initialize_main_page()
            recommendations = self.recommender.recommend(limit=20)
            self.display_anime_list(recommendations)

    def _logout(self) -> None:
        """This function is associated with the log out button.
        It attempts to log a user out of the system.
        If the attempt is unsuccessful, an error message box is displayed.
        """
        if not self.recommender.log_out():
            tk.messagebox.showerror("Error", "No user is logging in.")
        else:
            self._display_login_window()

    def _register_new_user(self) -> None:
        """This function is associated with the register button.
        It attempts to register for a new user.
        If the attempt is unsuccessful, an error message box is displayed.
        """

        username = self.username_entry.get()
        if not str.isalnum(username):
            tk.messagebox.showerror("Invalid username.", "The username can only contain letters or"
                                                         "numbers.")
        else:
            birthday = self.birth_month_var.get() + ' ' + self.birth_date_var.get() + ', ' + \
                       self.birth_year_var.get()
            gender = self.gender_var.get()
            # When then registering is successful
            if self.recommender.register(username, gender, birthday, self.profiles_file):
                tk.messagebox.showinfo(title="Successful", message="Successfully registered. "
                                                                   "You can log in now.")
                self._display_login_window()
            else:
                tk.messagebox.showerror("User already exists",
                                        "The username already exists. "
                                        "You should try a different one.")

    def _clear_main_canvas(self) -> None:
        """Helper function. Clear the main canvas to display new
        recommendations or search result."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.anime_covers = []


if __name__ == '__main__':

    app = Application('Data/animes.csv', 'Data/profiles.csv',
                      'Data/reviews.csv')
    app.run()
