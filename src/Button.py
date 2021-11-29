import pygame

class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, img_file, scale, label, genre = None, id = None):
        '''
        assigns all initial values to a button object and creates its image
        Args:
            x (int) - x pos of button
            y (int) - y pos of button
            img_file (int) - image file that gets loaded
            label (str) - text that goes on top of the image
            genre (str) - movie genre if it is a genre button
            id (int) - genre id of the genre
        return: none
        '''
        super().__init__()
        #rectangle and surface
        self.image = pygame.image.load(img_file).convert_alpha()
        self.rect = self.image.get_rect()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect.x = x
        self.rect.y = y
        #scale
        self.scale = scale
        self.image = pygame.transform.scale(self.image, (int(self.width * self.scale), int(self.height * self.scale)))
        #button label & data
        self.label = str(label)
        self.text = pygame.font.SysFont(None, 27)
        self.message = self.text.render(self.label, True, (255, 255, 255))
        self.message_rect = self.message.get_rect(center=(self.width / 2, self.height/2))
        self.image.blit(self.message, self.message_rect)
        self.id = id
        self.genre = genre

    def update(self, y):
        '''
        updates the position of the button to new values
        Args:
            y (int) new y pos
        Return: none
        '''
        self.y = y
        self.rect.y += self.y
