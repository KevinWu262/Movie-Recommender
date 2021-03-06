import pygame
import sys
import webbrowser
import requests
from src import Button
from src import APIrequest
class Controller:
    def __init__(self, tempdir):
        super().__init__()
        self.checkInternet()
        self.width = 1080
        self.height = 720
        self.state = "MAIN"
        pygame.display.set_caption("SuggestCinema")
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.background = pygame.Surface((1080, 14400))
        self.screen.fill((130, 210, 220)) #background color
        self.genre_list = pygame.sprite.Group()
        self.user_genre_buttons = pygame.sprite.Group()
        self.google_search_button = pygame.sprite.Group()
        self.user_genre_list = []
        self.user_selected_ids = []
        self.tempdir = tempdir
        self.connection_event = pygame.USEREVENT
        raw_genre_list = APIrequest.APIrequest.getId(self)
        # setting up buttons
        x_pos = 467
        y_pos = 0
        self.y_limit = 0
        for genre in raw_genre_list:
            y_pos += 55
            self.genre_list.add(Button.Button(x_pos, y_pos, "assets/buttonicon.png", 1, genre['name'], genre['name'], genre['id']))
        self.exit_button = Button.Button(900, 600, "assets/buttonicon.png", 1, "Exit")
        self.search_button = Button.Button(900, 400, "assets/buttonicon.png", 1, "Search")
        self.back_button = Button.Button(900, 500, "assets/buttonicon.png", 1, "Back")
        self.logo = pygame.image.load('assets/screenlogo.png')
        self.tmdb_logo = pygame.image.load('assets/tmdblogo.png')
        #first screen
        self.first_screen_sprites = pygame.sprite.Group(tuple(self.genre_list) + (self.exit_button,) + (self.search_button,))
        #second screen
        self.second_screen_sprites = pygame.sprite.Group((self.google_search_button,) + (self.exit_button,) + (self.back_button,))

    def mainLoop(self):
        """
        Checks for the current state of the program, and changes subloops in respect to the state.
        args: None
        return: None
        """
        while self.state:
            pygame.time.set_timer(self.connection_event, 3000)
            if self.state == "MAIN":
                self.firstScreenLoop()
            elif self.state == "SECOND":
                self.secondScreenLoop()
            self.checkInternet()

    def firstScreenLoop(self):
        """
        Subloop for the first screen of the program, and runs when the game state is "MAIN"
        args: None
        return: None
        """
        x_pos = 15
        y_pos = 200
        while self.state == "MAIN":
            y_offset = 0
            #checking for events
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == self.connection_event:
                    self.checkInternet()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    #scrolling
                    if event.button == 4 and self.y_limit > 0:
                        y_offset += 15
                        self.y_limit -= 15
                    if event.button == 5 and self.y_limit < 390:
                        y_offset -= 15
                        self.y_limit += 15
                    #exit button
                    if self.exit_button.rect.collidepoint(event.pos) and pygame.mouse.get_pressed()[0] == 1:
                            sys.exit()
                    #search button
                    elif self.search_button.rect.collidepoint(event.pos):
                        if pygame.mouse.get_pressed()[0] == 1:
                            self.state = "SECOND"
                    #center genre buttons
                    for button in self.genre_list:
                        if button.rect.collidepoint(event.pos) and pygame.mouse.get_pressed()[0] == 1:
                            if button.label in self.user_genre_list:
                                pass
                            elif button not in self.user_genre_buttons:
                                button_var = Button.Button(x_pos, y_pos, 'assets/buttonicon.png', 1, button.label, button.label, button.id)
                                self.user_genre_buttons.add(button_var)
                                self.user_genre_list.append(button.label)
                                self.user_selected_ids.append(button.id)
                                # printing for testing purposes
                                # print(self.user_genre_list)
                                # print(self.user_selected_ids)
                    #left side buttons
                    y_pos = 200
                    for button in self.user_genre_buttons:
                        if button.rect.collidepoint(event.pos) and pygame.mouse.get_pressed()[0] == 1:
                            button.kill()
                            self.user_genre_list.remove(button.label)
                            self.user_selected_ids.remove(button.id)
                            # printing for testing purposes
                            # print(self.user_genre_list)
                            # print(self.user_selected_ids)
                        else:
                            button.rect.y = y_pos
                            y_pos += 55

            #update
            self.screen.fill((130, 210, 220))
            self.screen.blit(self.logo, (150, 0))
            self.screen.blit(self.tmdb_logo, (850, 20))
            for button in self.genre_list:
                button.update(y_offset)
            self.first_screen_sprites.draw(self.screen)
            self.user_genre_buttons.draw(self.screen)

            #draw
            pygame.display.update()

    def secondScreenLoop(self):
        """
        Subloop for the second screen of the program, and runs when the game state is "SECOND", displays movie data
        based on chosen genres from the first screen. Movie data is blitted onto the background. Background moves
        up and down on y-axis based on scroll wheel input.
        args: None
        return: None
        """
        #retrieving movie data
        x_pos = 12  #x position for buttons
        y_pos = 250 #y position for buttons
        y_pos_screen = 0 #y position for screen
        current_iter = 0
        movie_data = APIrequest.APIrequest(self.user_selected_ids)
        results = movie_data.apiRequest()
        results_list = results['results']
        provider_list = []
        for button in self.google_search_button:
            button.kill()
        for movie in results_list:
            current_iter += 1
            temp_movie_id = movie['id']
            temp_providers = APIrequest.APIrequest.getProviders(self, temp_movie_id)
            provider_list.append(temp_providers)
            button = Button.Button(x_pos, y_pos, 'assets/buttonicon.png', 1, "Google Search", movie['title'])
            y_pos += 325    #if poster_y_pos changes, change this value by the same amount
            self.google_search_button.add(button)
        # print(provider_list)
        directory = f'assets/{self.tempdir}/'
        movie_data.getPosters(results, directory)
        while self.state == "SECOND":
            #check for events
            y_offset = 0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == self.connection_event:
                    self.checkInternet()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    #exit button
                    if self.exit_button.rect.collidepoint(event.pos) and pygame.mouse.get_pressed()[0] == 1:
                        sys.exit()
                    #back button
                    if self.back_button.rect.collidepoint(event.pos) and pygame.mouse.get_pressed()[0] == 1:
                        self.state = "MAIN"
                    #google search buttons
                    for button in self.google_search_button:
                        if button.rect.collidepoint(event.pos) and pygame.mouse.get_pressed()[0] == 1:
                            webbrowser.open(f'https://www.google.com/search?q={button.genre}')
                    #scrolling
                    if event.button == 4 and y_pos_screen < 0:
                        y_pos_screen += 150
                        y_offset += 150
                    if event.button == 5 and y_pos_screen > -5750:
                        y_pos_screen -= 150
                        y_offset -= 150

            #update
            title_font = pygame.font.SysFont('arial', 30, True)
            standard_font = pygame.font.SysFont('arial', 15)
            y_pos = 0   #starting y position for all items being blitted
            x_pos = 200 #starting x position for text
            poster_y_pos = 0
            current_iter = 0
            self.screen.fill((130, 210, 220))
            self.background.fill((130, 210, 220))
            self.background.blit(self.logo, (850, 0))
            self.background.blit(self.tmdb_logo, (850, 200))
            #movie data
            for movie in results_list:
                items = []
                temp_title = movie['title']
                temp_date = movie['release_date']
                temp_avg_vote = movie['vote_average']
                temp_vote_count = movie['vote_count']
                temp_provider = provider_list[current_iter]
                temp_description = movie['overview']
                temp_description_list = []
                ch_accum = 0
                total_accum = 0
                description_str = ""
                str_len = len(temp_description)
                #pygame doesn't allow multi line text, lines 211 - 222 splits the text into strings of 110
                #characters, and adds the splitted text into a list
                for ch in temp_description:
                    total_accum += 1
                    if total_accum == str_len:
                        temp_description_list.append(description_str)
                    elif ch_accum < 110:    #maximum number of characters per line, numbers in line 216 and 219 must be the same
                        description_str += ch
                        ch_accum += 1
                    elif ch_accum >= 110:
                        description_str += ch
                        temp_description_list.append(description_str)
                        description_str = ""
                        ch_accum = 0
                current_iter += 1
                #converting data from API into strings and formatting them for the program
                convert_str = [temp_date, temp_avg_vote, temp_vote_count, temp_provider]
                for i in convert_str:
                    str(i)
                date = f'Release Date: {temp_date}'
                avg_vote = f'Average Rating: {temp_avg_vote} / 10'
                vote_count = f'Vote Count: {temp_vote_count}'
                provider = f'Streaming On: {temp_provider}'
                #order temp_items is in determines order on screen
                temp_items = [
                    date,
                    avg_vote,
                    vote_count,
                    provider,
                ]
                #displaying movie data and posters
                title = title_font.render(temp_title, True, (0, 0, 0))
                for i in temp_items:
                    temp = standard_font.render(i, True, (0, 0, 0))
                    items.append(temp)
                self.background.blit(title, (x_pos, y_pos))
                y_pos += 40 #text spacing between title and movie details
                for item in items:
                    self.background.blit(item, (x_pos, y_pos))
                    y_pos += 20 #text spacing for each movies details
                y_pos += 10
                #blitting each line created from lines 211 - 212
                for line in temp_description_list:
                    temp_line = standard_font.render(line, True, (0, 0, 0))
                    self.background.blit(temp_line, (x_pos, y_pos))
                    y_pos += 20
                y_pos -= 10
                for line in temp_description_list:
                    y_pos -= 20
                y_pos += 205   #text spacing between movies, if poster_y_pos changes, change this value by the same amount
                #blitting posters
                poster = pygame.image.load(f'assets/{self.tempdir}/sample{current_iter-1}.jpg').convert_alpha()
                poster = pygame.transform.scale(poster, (167, 250))
                self.background.blit(poster, (0, poster_y_pos))
                poster_y_pos += 325 #poster spacing
            self.screen.blit(self.background, (0, y_pos_screen))
            for button in self.google_search_button:
                button.update(y_offset)
            self.second_screen_sprites.draw(self.screen)
            self.google_search_button.draw(self.screen)
            #redraw
            pygame.display.flip()

    def checkInternet(self):
        """
        Checks if the user has an internet connection, or if there is an issue with the API. For constant checking this
        function needs to be put in a while loop.
        args: None
        return: None
        """
        try:
            result = requests.get("https://api.themoviedb.org/3/discover/movie?",
                                  params={'api_key': 'ae2a71b3aac0b67e745c46b2ff92ecb9', 'with_genres': 18,
                                          'language': 'en-US'})
            if result.status_code != 200:
                print("If you are connected to the internet, try again later")
                sys.exit()
            else:
                pass
        except:
            print("Please Connect to the Internet")
            sys.exit()
