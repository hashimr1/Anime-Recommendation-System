"""CSC111 Final Project: My Anime Recommendations
==================================================================
The Application class

This module contains the class definition for the main application
using tkinter.
==================================================================
@authors: Tahseen Rana, Tu Pham
"""

import textwrap
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
import requests
from PIL import Image, ImageTk, UnidentifiedImageError

from recommendation_engine import RecommendationEngine
from data_loader import create_anime_graph_from_data
from anime_graph import Anime
from trie_auto_complete import Trie

##########################################################################
# ==========  The default dimensions of GUI components  ================ #
##########################################################################

# The dimensions of the main window
HEIGHT = '768'
WIDTH = '1360'
WINDOW_DIM = WIDTH + 'x' + HEIGHT

# The dimensions of the settings window
SETTINGS_HEIGHT = '180'
SETTINGS_WIDTH = '240'
SETTINGS_DIM = SETTINGS_WIDTH + 'x' + SETTINGS_HEIGHT

# The limit of the numbers of anime get displayed on screen
ANIME_DISPLAY_LIMIT = 50

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
TITLE_FONT = ("Courier", 18)
GRAY = '#E3E2E2'
RED = '#FF2D00'

# ======================================================================= #
###########################################################################


class Application(tk.Tk):
    """The Main application.
    Instance Attributes:
        - background_image: a reference to the background image. We need to keep references to
        tk Images so that the garbage collector doesn't destroy them.
        - perm_anime_covers: a list of references to anime cover images that is being held
        until the user log out.
        - temp_anime_covers: a list of references to temporary anime cover images that is used
        for search result, anime info pages.
        - content_canvas: The Canvas object on which content like recommendation is draw on.
        - perm_content_frame: The permanent content frame inside the content canvas. This act
        as a "window"—a child object of the canvas, for drawing content on. We need it to
        implement the scrollbar.
        - temp_content_frame: Same as perm_content_frame. This frame is to display
        temporary content.
        - perm_frame_id: The representative id of the permanent frame associated with the
        content canvas. We need this to tell the canvas which frame to show and which to hide.
        - temp_frame_id: Similar to perm_frame_id.
        - query: The StringVar associated with the search bar. We keep it as an instance attribute
        to trace it.
        - selected_genre: The StringVar associated with the genre dropdown. Purpose is similar
        to query.
        - output_mode: Current output mode of the application. (Simplified or Complete).
        - current_user: The user currently logged in.
        - trie: The trie for autocompletion feature.
        - anime_file: path to the anime data file.
        - profiles_file: path to the profiles file.
        - reviews_file: path to the reviews file.
    """
    # The GUI components necessary for input/output
    background_image: tk.PhotoImage
    perm_anime_covers: list[tk.PhotoImage]
    temp_anime_covers: list[tk.PhotoImage]
    content_canvas: tk.Canvas
    perm_content_frame: tk.Frame
    temp_content_frame: tk.Frame
    perm_frame_id: int
    temp_frame_id: int

    query: tk.StringVar
    selected_genre: tk.StringVar

    style: ttk.Style
    output_mode: str
    current_user: Optional[str]

    # Components for computations
    trie: Trie
    recommender: RecommendationEngine
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
        self.perm_anime_covers = []
        self.temp_anime_covers = []
        self.current_user = None
        # Initializing the recommendation engine
        graph = create_anime_graph_from_data(self.anime_file, self.profiles_file,
                                             self.reviews_file)
        self.trie = Trie(graph.fetch_all_anime_names())
        self.recommender = RecommendationEngine(graph)

        # Initializing the GUI
        self.title('My Anime List')
        self.geometry(WINDOW_DIM)

        # Setting the style
        self.style = ttk.Style(self)
        self.tk.call('source', 'tk_theme/azure-dark.tcl')
        self.style.theme_use('azure-dark')
        self.output_mode = 'Complete'

        # Load the background image for later use
        self.background_image = tk.PhotoImage(file='anime_wallpaper.png')

    def run(self) -> None:
        """Run the app."""
        self._display_login_window()
        self.mainloop()

    def _search_after_timer(self, last_keyword: str) -> None:
        """This function is intended to be executed after an user
        type something on the search bar.
        It checks to see whether the search query has stayed the same. If yes, a search
        is performed and the result is displayed on the canvas."""
        keyword = self.query.get()
        if last_keyword == keyword:
            anime_names = self.trie.all_suffixes(keyword)
            anime_names.sort(key=lambda word: word.lower())
            animes_so_far = []
            for name in anime_names:
                anime = self.recommender.fetch_anime_by_name(name)
                if anime is not None:
                    animes_so_far.append(anime)
                    if len(animes_so_far) > ANIME_DISPLAY_LIMIT:
                        break

            self._clear_frame(self.temp_content_frame)
            self._switch_canvas_display_to(self.temp_content_frame)
            self._display_anime_list(self.temp_content_frame, "Search results: ", animes_so_far)

    def _on_query(self, *args) -> None:  # args is passed to the callback, but we don't use them
        """This is a callback associated with the search bar. It is called everytime something is
        typed on the search bar.
        It will set a timer, which activates _search_after_timer after sometimes.
        """
        keyword = self.query.get()
        if keyword == '':
            self._clear_frame(self.temp_content_frame)
            self._switch_canvas_display_to(self.perm_content_frame)
            return
        else:
            self.after(1200, self._search_after_timer, keyword)

    def _filter_by_genre(self, *args) -> None:
        """Callback associated with the genre drop down.
        This function display a list of 30 most popular anime by genre on the temporary content
        frame.
        """
        selected_genre = self.selected_genre.get()
        if selected_genre == 'All Genres':
            return

        self._clear_frame(self.temp_content_frame)
        self._switch_canvas_display_to(self.temp_content_frame)

        def _on_go_back() -> None:
            """The callback for the 'back to main page' button.
            Reset the genre dropdown and go back to main page.
            """
            self.selected_genre.set(value='All Genres')
            self._switch_canvas_display_to(self.perm_content_frame)

        ttk.Button(self.temp_content_frame, text='Back to Main Page',
                   command=_on_go_back).pack(anchor=tk.NW)

        anime_list = self.recommender.fetch_popular_by_genre(selected_genre, 30)
        self._display_anime_list(self.temp_content_frame,
                                 "Most popular " + selected_genre + " anime:", anime_list)

    def _initialize_main_page(self) -> None:
        """Initialize the components of the main page."""
        # Setting up the search bar
        self.query = tk.StringVar()
        self.query.trace_add('write', self._on_query)
        search_bar = ttk.Entry(self, textvariable=self.query)
        search_bar.place(relx=LEFT_MARGIN, rely=TOP_MARGIN, relheight=0.04, relwidth=0.7)

        # Initializing the content frame
        self._initialize_content_box()

        # The genre dropdown
        all_genres = self.recommender.fetch_all_genres()
        self.selected_genre = tk.StringVar()
        genre_dropdown = ttk.OptionMenu(self, self.selected_genre, 'All Genres', *all_genres)
        genre_dropdown.place(relx=0.725, rely=TOP_MARGIN)
        self.selected_genre.trace_add('write', self._filter_by_genre)

        # Setting button in the corner
        settings_button = ttk.Button(self, text='Settings', command=self._display_settings)
        settings_button.place(relx=0.92, rely=TOP_MARGIN, anchor=tk.NE)
        # The logout button
        logout_button = ttk.Button(self, text='Logout', command=self._logout)
        logout_button.place(relx=1.0 - LEFT_MARGIN, rely=TOP_MARGIN, anchor=tk.NE)
        # Creating the content to display to user
        self._generate_new_content()

    def _generate_new_content(self) -> None:
        """Clear the content box, generate new recommendation, and display them."""
        # Wipe out the old permanent content.
        self._clear_frame(self.perm_content_frame)
        self._switch_canvas_display_to(self.perm_content_frame)
        # A text display to let the user know that the system is doing something
        wait_label = ttk.Label(self.perm_content_frame, text="One moment...", font=TITLE_FONT)
        wait_label.pack(anchor=tk.NW)
        self.update_idletasks()

        # Generating new recommendations
        recommendations = self.recommender.recommend(self.current_user, limit=20)
        if len(recommendations) > 0:
            self._display_anime_list(self.perm_content_frame,
                                     "Recommended for You:", recommendations)

        newly_released = self.recommender.fetch_new_anime(limit=12)
        self._display_anime_list(self.perm_content_frame,
                                 "Newly Released Anime", newly_released)
        most_popular = self.recommender.fetch_popular_anime(limit=12)
        self._display_anime_list(self.perm_content_frame,
                                 "Most Popular on MyAnimeList", most_popular)
        wait_label.destroy()

    def _initialize_content_box(self) -> None:
        """Initialize the box containing the main content that is to be shown to the user,
        including recommendations, search results...
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

        # Set up the frames for displaying main content
        self.perm_content_frame = ttk.Frame(self.content_canvas)
        self.temp_content_frame = ttk.Frame(self.content_canvas)
        self.perm_content_frame.bind('<Configure>',
                                     lambda _: self.content_canvas.configure(
                                         scrollregion=self.content_canvas.bbox('all')))

        # Also create a hidden window for the temporary content
        self.temp_frame_id = self.content_canvas.create_window((0, 0), state='hidden',
                                                               window=self.temp_content_frame,
                                                               anchor=tk.NW)
        # Creating a "window" which is represented by the frame inside the canvas.
        self.perm_frame_id = self.content_canvas.create_window((0, 0),
                                                               window=self.perm_content_frame,
                                                               anchor=tk.NW)

        def _on_mouse_wheel(event: tk.Event) -> None:
            """The callback for the scrollbar."""
            self.content_canvas.yview_scroll(-1 * int((event.delta / 120)), "units")
            self.update_idletasks()

        self.content_canvas.bind_all("<MouseWheel>", _on_mouse_wheel)

    def _display_anime_list(self, frame: tk.Frame, list_title: str,
                            anime_list: list[Anime]) -> None:
        """display a list of anime on the canvas.
        Preconditions:
            - self.perm_content_frame is initialized.
            - frame is self._perm_content_frame or frame is self._temp_content_frame
        """
        # Choose which list of to keep a reference of the anime covers
        cover_list = self.perm_anime_covers \
            if frame is self.perm_content_frame else self.temp_anime_covers

        # Make the title
        title = ttk.Label(frame, font=TITLE_FONT, text=list_title)
        title.pack(pady=10, anchor=tk.NW)
        # Create a frame to contain the list
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.X)
        if self.output_mode == 'Complete':
            # starts displaying the anime in the list
            for i in range(len(anime_list)):
                col = i % 7
                row = i // 7
                anime = anime_list[i]
                anime_title = anime.title
                if len(anime_title) > 24:
                    anime_title = textwrap.fill(anime_title, 24)

                try:
                    im = Image.open(requests.get(anime.image_url, stream=True).raw)
                    im = im.resize((149, 233))
                    cover_im = ImageTk.PhotoImage(im)
                except UnidentifiedImageError:
                    cover_im = ImageTk.PhotoImage(Image.open("image_loading_error.jpg"))

                # Keep a reference to the image so it doesn't get destroyed after function return.
                cover_list.append(cover_im)

                # Create a "button" that display the aime
                button = ttk.Button(list_frame, text=anime_title, image=cover_im, compound='top',
                                    command=lambda anime=anime: self._display_anime_info(anime))
                button.grid(row=row, column=col, padx=6, pady=4, sticky=tk.NSEW)
        else:
            for anime in anime_list:
                anime_title = anime.title
                button = ttk.Button(list_frame, text=anime_title, width=60,
                                    command=lambda anime=anime: self._display_anime_info(anime))
                button.pack(pady=2, anchor=tk.NW)

    def _display_anime_info(self, anime: Anime) -> None:
        """Display the info page of an anime on the main content canvas.
        """
        self._clear_frame(self.temp_content_frame)
        self._switch_canvas_display_to(self.temp_content_frame)
        # Requesting anime cover image from the internet.
        try:
            im = Image.open(requests.get(anime.image_url, stream=True).raw)
            cover_im = ImageTk.PhotoImage(im)
        except UnidentifiedImageError:
            cover_im = ImageTk.PhotoImage(Image.open("image_loading_error.jpg"))
        # Keep a reference of the image so it doesn't get destroyed by the garbage collector.
        self.temp_anime_covers.append(cover_im)

        # A frame for the image and a few buttons on the left side
        image_button_frame = ttk.Frame(self.temp_content_frame)
        image_button_frame.pack(side=tk.LEFT)
        # Display the cover image
        ttk.Label(image_button_frame, image=cover_im).pack()

        # the reviewing button and dropdown
        ttk.Label(image_button_frame, text="Make a review: ").pack(pady=5)
        review_frame = ttk.Frame(image_button_frame)
        review_frame.pack(pady=5)
        possible_scores = [str(i) for i in range(1, 11)]
        selected_review_score = tk.StringVar()
        ttk.OptionMenu(review_frame, selected_review_score,
                       *possible_scores).pack(side=tk.LEFT, padx=4)
        submit_button = ttk.Button(review_frame,
                                   text='Submit Review',
                                   command=lambda:
                                   self._create_review(anime.uid,
                                                       float(selected_review_score.get())))
        submit_button.pack(side=tk.LEFT, padx=10)
        # The "Go back" button
        back = ttk.Button(image_button_frame, text='Go back',
                          command=lambda: self._switch_canvas_display_to(self.perm_content_frame))
        back.pack(pady=80, anchor=tk.SW)

        # The info frame on right side
        info_frame = ttk.Frame(self.temp_content_frame)
        info_frame.pack(side=tk.LEFT, padx=10, pady=4, anchor=tk.NW)
        # Anime name
        ttk.Label(info_frame, text="Title: " + anime.title).pack(pady=5, anchor=tk.NW)
        # Aired date
        if anime.aired_date.year == 1900:
            aired_text = "Not Available."
        else:
            aired_text = anime.aired_date.strftime('%B %d, %Y')
        ttk.Label(info_frame, text="Aired: " + aired_text).pack(pady=5, anchor=tk.NW)
        # Number of episodes
        ttk.Label(info_frame,
                  text="Number of episodes: " + str(anime.total_episodes)).pack(pady=5,
                                                                                anchor=tk.NW)
        # Score
        ttk.Label(info_frame, text="Score: " + str(anime.score)).pack(pady=5, anchor=tk.NW)
        # Ranking in score
        ttk.Label(info_frame, text="Score Ranking: #" + str(anime.rank)).pack(pady=5, anchor=tk.NW)
        # Ranking in popularity
        ttk.Label(info_frame, text="Popularity: #" + str(anime.popularity)).pack(pady=5,
                                                                                 anchor=tk.NW)
        # Genres
        genre_list = [str(genre) for genre in anime.neighbor_genres]
        genres = ', '.join(genre_list)
        ttk.Label(info_frame, text='Genres: ' + genres).pack(pady=5, anchor=tk.NW)
        # Synopsis
        synopsis = textwrap.fill(anime.synopsis, 180)
        ttk.Label(info_frame, text="Synopsis: " + synopsis).pack(pady=5, anchor=tk.NW)

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
        username_entry = ttk.Entry(register_frame)
        username_entry.pack(pady=10)

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
        gender_var = tk.StringVar()   # The variable for the option
        gender_dropdown = ttk.OptionMenu(gender_frame, gender_var, 'Male', 'Female', 'Other')
        gender_dropdown.pack(side='left')

        # The date of birth section
        date_birth_frame = ttk.Frame(register_frame)
        date_birth_frame.pack()
        birth_label = ttk.Label(date_birth_frame, text='Date of Birth (month, day, year):')
        birth_label.pack(pady=10)
        # Month
        birth_month_var = tk.StringVar()
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug',
                  'Sept', 'Oct', 'Nov', 'Dec']
        month_dropdown = ttk.OptionMenu(date_birth_frame, birth_month_var, *months)
        month_dropdown.pack(side=tk.LEFT)

        # Day
        birth_date_var = tk.StringVar()
        day = [str(x) for x in range(1, 32)]
        day_dropdown = ttk.OptionMenu(date_birth_frame, birth_date_var, *day)
        day_dropdown.pack(side=tk.LEFT, padx=10)

        # Year
        birth_year_var = tk.StringVar()
        year = [str(y) for y in range(2021, 1920, -1)]
        year_dropdown = ttk.OptionMenu(date_birth_frame, birth_year_var, *year)
        year_dropdown.pack(side=tk.RIGHT)

        # The buttons (back/register)
        button_frame = tk.Frame(register_frame)
        button_frame.pack(pady=20)
        back_button = ttk.Button(button_frame, text='Back',
                                 command=self._display_login_window)
        back_button.pack(side=tk.LEFT, padx=6)

        def _on_register() -> None:
            """The callback associated with the register button."""
            self._register_new_user(username_entry.get(), birth_month_var,
                                    birth_date_var, birth_year_var, gender_var)

        register_button = ttk.Button(button_frame, text='Register',
                                     command=_on_register)
        register_button.pack(side=tk.LEFT, padx=6)

    def _display_login_window(self) -> None:
        """Login window to let users login."""
        for widget in self.winfo_children():
            widget.destroy()

        background_label = tk.Label(self, image=self.background_image)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Setting button in the corner
        settings_button = ttk.Button(self, text='Settings', command=self._display_settings)
        settings_button.place(relx=1.0 - LEFT_MARGIN, rely=TOP_MARGIN, anchor=tk.NE)

        login_frame = ttk.Frame(self)
        login_frame.place(relx=0.5, rely=0.5, relwidth=0.16, relheight=0.36, anchor=tk.CENTER)
        # Username
        username_label = ttk.Label(login_frame, text='Username:')
        username_label.pack(pady=10)
        username_entry = ttk.Entry(login_frame)
        username_entry.pack(pady=10)
        # Password
        password_label = ttk.Label(login_frame, text='Password:')
        password_label.pack(pady=10)
        password_entry = ttk.Entry(login_frame)
        password_entry.pack(pady=10)

        # Aligning the buttons
        button_frame = ttk.Frame(login_frame)
        button_frame.pack(pady=20, padx=10)
        login_button = ttk.Button(button_frame, text='Login',
                                  command=lambda: self._login(username_entry.get()))
        login_button.pack(side=tk.LEFT, padx=5)

        register_button = ttk.Button(button_frame, text='Register',
                                     command=self._display_register_window)
        register_button.pack(side=tk.LEFT, padx=5)

    def _display_settings(self) -> None:
        """Display a setting window"""
        win = tk.Toplevel(self)
        win.wm_title("Settings")
        win.geometry(SETTINGS_DIM)

        setting_options = ttk.Frame(win)
        setting_options.pack(pady=10)

        selected_option = tk.StringVar(setting_options)
        mode_dropdown = ttk.OptionMenu(setting_options, selected_option,
                                       'Output mode', 'Simplified', 'Complete')
        mode_dropdown.pack(anchor=tk.CENTER, pady=10)

        confirm_options = ttk.Frame(win)
        confirm_options.pack(pady=40)

        def on_confirm() -> None:
            """Callback for the 'Apply' button."""
            selected = selected_option.get()
            if selected not in {'Output mode', self.output_mode}:
                self.output_mode = selected
                if self.current_user is not None:
                    self._generate_new_content()
            win.destroy()

        confirm_button = ttk.Button(confirm_options, text='Apply', command=on_confirm)
        cancel_button = ttk.Button(confirm_options, text='Cancel', command=win.destroy)
        confirm_button.pack(side=tk.LEFT, padx=10)
        cancel_button.pack(side=tk.LEFT, padx=10)

    def _login(self, username: str) -> None:
        """This function is associated with the log in button in the login window.
        It attempts to log a user in the system.
        If the attempt is unsuccessful, an error message box is displayed.
        """
        if not self.recommender.check_user_exists(username):
            tk.messagebox.showerror("Login unsuccessful",
                                    "The username does not exist. Please try again.")
        else:
            self.current_user = username
            self._initialize_main_page()

    def _logout(self) -> None:
        """This function is associated with the log out button.
        It attempts to log a user out of the system.
        If the attempt is unsuccessful, an error message box is displayed.
        """
        self.current_user = None
        self._display_login_window()

    def _register_new_user(self, username: str, birth_month_var: tk.StringVar,
                           birth_date_var: tk.StringVar, birth_year_var: tk.StringVar,
                           gender_var: tk.StringVar) -> None:
        """This function is associated with the register button.
        It attempts to register for a new user.
        If the attempt is unsuccessful, an error message box is displayed.
        """
        if not str.isalnum(username):
            tk.messagebox.showerror("Invalid username.", "The username can only contain letters or"
                                                         " numbers.")
        else:
            birthday = birth_month_var.get() + ' ' + birth_date_var.get() + ', ' + \
                birth_year_var.get()
            gender = gender_var.get()
            # When then registering is successful
            if self.recommender.register(username, gender, birthday, self.profiles_file):
                tk.messagebox.showinfo(title="Successful", message="Successfully registered. "
                                                                   "You can log in now.")
                self._display_login_window()
            else:
                tk.messagebox.showerror("User already exists",
                                        "The username already exists. "
                                        "You should try a different one.")

    def _create_review(self, anime_uid: int, review_score: float) -> None:
        """Add a new review to the system. This is a callback associated with the submit review
        button.
        Preconditions:
            - self.current_user is not None
        """
        self.recommender.add_review(self.current_user, anime_uid,
                                    review_score,
                                    self.reviews_file)
        result = tk.messagebox.askyesno("Successful",
                                        "Successfully added a new review. "
                                        "Do you want the system to generate new recommendations?")
        if result is True:
            self._switch_canvas_display_to(self.perm_content_frame)
            self._generate_new_content()

    def _clear_frame(self, frame: tk.Frame) -> None:
        """Helper function. Clear the given frame. If that frame is one of the two main content
        frames, clear the associated list of image references as well."""
        if frame is self.perm_content_frame:
            self.perm_anime_covers = []
        elif frame is self.temp_content_frame:
            self.temp_anime_covers = []

        for widget in frame.winfo_children():
            widget.destroy()

    def _switch_canvas_display_to(self, frame: tk.Frame) -> None:
        """Switch the display of the canvas from the temporary content frame to the permanent
        content frame or the vice versa.
        Preconditions:
            - frame is self.perm_content_frame or frame is self.temp_content_frame
        """

        # When the permanent content is being displayed
        if self.content_canvas.itemcget(tagOrId=self.perm_frame_id, option='state') == 'normal':
            if frame is self.perm_content_frame:
                return
            self.temp_content_frame.bind('<Configure>', lambda _: self.content_canvas.configure(
                scrollregion=self.content_canvas.bbox('all')))
            self.content_canvas.yview_moveto('0.0')
            self.content_canvas.itemconfigure(self.perm_frame_id, state='hidden')
            self.content_canvas.itemconfigure(self.temp_frame_id, state='normal')

        else:  # When the permanent content is hidden
            if frame is self.temp_content_frame:
                return
            self.perm_content_frame.bind('<Configure>', lambda _: self.content_canvas.configure(
                scrollregion=self.content_canvas.bbox('all')))
            self.content_canvas.itemconfigure(self.perm_frame_id, state='normal')
            self.content_canvas.itemconfigure(self.temp_frame_id, state='hidden')
