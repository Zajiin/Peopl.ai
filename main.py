import sys
import pygame
import pygame_textinput
import time
import openai
from pygame.locals import QUIT, VIDEORESIZE
from pygame_textinput import TextInputManager, TextInputVisualizer

# ===================== FOUND ONLINE =====================
class Button:  # Handles Clickable Buttons
    def __init__(self, text, width, height, pos, elevation):
        # Core attributes
        self.pressed = False
        self.elevation = elevation
        self.dynamic_elevation = elevation
        self.original_y_pos = pos[1]
        self.menu = False
        self.ready = False
        self.width = width
        self.height = height

        # Top rectangle
        self.top_rect = pygame.Rect(pos, (width, height))
        self.top_color = '#D0000C'

        # Bottom rectangle
        self.bottom_rect = pygame.Rect(pos, (width, height))
        self.bottom_color = '#C2000B'

        # Text
        self.text = text
        self.text_surf = gui_font.render(text, True, '#FFFFFF')
        self.text_rect = self.text_surf.get_rect(center=self.top_rect.center)

        buttons.append(self)

    def draw(self):
        # Elevation logic
        self.top_rect.y = self.original_y_pos - self.dynamic_elevation
        self.text_rect.center = self.top_rect.center

        self.bottom_rect.midtop = self.top_rect.midtop
        self.bottom_rect.height = self.top_rect.height + self.dynamic_elevation

        pygame.draw.rect(displaySurface, self.bottom_color, self.bottom_rect, border_radius=12)
        pygame.draw.rect(displaySurface, self.top_color, self.top_rect, border_radius=12)
        displaySurface.blit(self.text_surf, self.text_rect)
        self.check_click()

    def check_click(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.top_rect.collidepoint(mouse_pos):
            self.top_color = '#F2000E'
            if pygame.mouse.get_pressed()[0]:
                self.dynamic_elevation = 0
                self.pressed = True
                if self.pressed and self.ready:
                    self.ready = False
                    self.menu = True
            else:
                self.dynamic_elevation = self.elevation
                if self.pressed:
                    self.pressed = False
                self.ready = True
        else:
            self.dynamic_elevation = self.elevation
            self.top_color = '#D0000C'
            self.bottom_color = '#C2000B'
# ========================================================

class Image:  # Handles Images
    def __init__(self, filename, dimensions=(500, 500), border=False, border_width=10, border_radius=5, **kwargs):
        # Load the image into a rect
        self.surf = pygame.image.load(filename)
        self.surf = pygame.transform.scale(self.surf, dimensions)
        self.rect = self.surf.get_rect()

        # Set the **kwargs into a variable
        self.kwargs = kwargs

        # Properties of the background border
        self.border = border
        self.border_rect = None
        self.border_radius = border_radius
        self.border_width = border_width
        self.border_color = '#D0000C'

        # Set the position of the image
        self.set_pos(self.kwargs)

    def set_pos(self, kwargs):  # Sets the position of the image
        for key, value in kwargs.items():
            if key == "center":
                try:
                    self.rect = self.surf.get_rect(center=value)
                except TypeError:
                    raise RuntimeError("Not a valid tuple")
            elif key == "topleft":
                self.rect = self.surf.get_rect(topleft=value)
            else:
                raise RuntimeError("Not a valid kwargs.")

        self.border_rect = self.rect.copy().inflate(self.border_width, self.border_width)

    def display_image(self):  # Displays the image (and border)
        if self.border:
            pygame.draw.rect(displaySurface, self.border_color, self.border_rect, self.border_radius)

        displaySurface.blit(self.surf, self.rect)


class Text:  # Handles text
    def __init__(self, text="", text_antialias=False, color=(255, 255, 255), **kwargs):
        self.font = pygame.font.Font(None, 50)
        self.text = text
        self.text_antialias = text_antialias
        self.color = color
        self.render = self.font.render(self.text, self.text_antialias, self.color)

        # Initialize class attributes and assign kwargs
        self.width = 0
        self.height = 0
        self.pos = (0, 0)
        self.kwargs = kwargs

        # Set the position of the text
        self.set_pos(self.kwargs)

    def set_pos(self, kwargs):
        for key, value in kwargs.items():
            if key == "center":
                try:
                    self.width = self.render.get_width()
                    self.height = self.render.get_height()
                    self.pos = (value[0] - (self.width // 2), value[1] - (self.height // 2))
                except TypeError:
                    raise RuntimeError("Not a valid tuple")
            elif key == "topleft":
                self.pos = value
            else:
                raise RuntimeError("Not a valid kwargs.")

    def display_text(self):  # Displays text
        displaySurface.blit(self.render, self.pos)


# Initialize pygame
pygame.init()

# Create the list for the buttons class
buttons = []

# Custom font size
gui_font = pygame.font.Font(None, 50)

# Menu Screen Buttons
buttonHist = Button('Historical Figures', 300, 75, (10, 650), 5)
buttonCeleb = Button('Present-Day Celebrities', 425, 75, (320, 650), 5)

# Choice Screen Buttons
buttonPrev = Button('Prev', 120, 75, (120, 650), 5)
buttonMenu = Button('Menu', 120, 75, (250, 650), 5)
buttonSel = Button('Select', 120, 75, (380, 650), 5)
buttonNext = Button('Next', 120, 75, (510, 650), 5)

# User Input Screen Buttons
buttonBack = Button('Back', 120, 75, (25, 650), 5)

# Maximum character text for User Input Screen
maxCharText = Text("MAX CHARACTERS", color=(255, 0, 0), topleft=(285, 668))

# Settings and Variable initialization
size = (750, 750)
screenCol = (0, 0, 0)

inputCategory = ''
userInput = ""
currentCharacter = ""
currentName = ""

msgDisplayed = []
msgDisplayedMax = 22

msgHistory = []
msgHistoryMax = 50

msgPadding = 94
msgSpacing = 25

# Used for changing images on the GUI
screenHist = 0
screenCeleb = 0

# Initialize the title screen png
titlescreen = Image("titlescreen.png", border=False, dimensions=(500, 250), center=(375, 300))

# List of names for text formatting
histNames = [
    "Albert Einstein",
    "Abraham Lincoln",
    "MLK Jr.",
    "Napoleon Bonaparte",
    "Nikola Tesla"
]

celebNames = [
    "Elon Musk",
    "Ronaldo",
    "The Rock",
    "Keanu Reeves",
    "Eminem"
]

# Lists containing / initializing images
largeHistImages = [
    Image("einstein.png", border=True, center=(375, 300)),
    Image("lincoln.png", border=True, center=(375, 300)),
    Image("martin.png", border=True, center=(375, 300)),
    Image("napoleon.png", border=True, center=(375, 300)),
    Image("nikola.png", border=True, center=(375, 300))
]

smallHistImages = [
    Image("einstein.png", (70, 70), True, 5, 2, topleft=(155, 650)),
    Image("lincoln.png", (70, 70), True, 5, 2, topleft=(155, 650)),
    Image("martin.png", (70, 70), True, 5, 2, topleft=(155, 650)),
    Image("napoleon.png", (70, 70), True, 5, 2, topleft=(155, 650)),
    Image("nikola.png", (70, 70), True, 5, 2, topleft=(155, 650))
]

largeCelebImages = [
    Image("elon.png", border=True, center=(375, 300)),
    Image("ronaldo.png", border=True, center=(375, 300)),
    Image("the rock.png", border=True, center=(375, 300)),
    Image("keanu.png", border=True, center=(375, 300)),
    Image("eminem.png", border=True, center=(375, 300))
]

smallCelebImages = [
    Image("elon.png", (70, 70), True, 5, 2, topleft=(155, 650)),
    Image("ronaldo.png", (70, 70), True, 5, 2, topleft=(155, 650)),
    Image("the rock.png", (70, 70), True, 5, 2, topleft=(155, 650)),
    Image("keanu.png", (70, 70), True, 5, 2, topleft=(155, 650)),
    Image("eminem.png", (70, 70), True, 5, 2, topleft=(155, 650))
]

# Lists containing / initializing text
screenHistText = [
    Text("Albert Einstein", center=(375, 600)),
    Text("Abraham Lincoln", center=(375, 600)),
    Text("Martin Luther King Jr.", center=(375, 600)),
    Text("Napoleon Bonaparte", center=(375, 600)),
    Text("Nikola Tesla", center=(375, 600))
]

screenCelebText = [
    Text("Elon Musk", center=(375, 600)),
    Text("Cristiano Ronaldo", center=(375, 600)),
    Text("Dwayne 'The Rock' Johnson", center=(375, 600)),
    Text("Keanu Reeves", center=(375, 600)),
    Text("Marshall 'Eminem' Mathers", center=(375, 600))
]

# Set the starting screen to the Main Menu
buttonMenu.menu = True

# Text_input setup
defaultTextCol = (255, 255, 255)
textinput = pygame_textinput.TextInputVisualizer()
manager = TextInputManager(validator=lambda input1: len(input1) <= 500)
font = pygame.font.SysFont("Calibri", 25)
textinput_custom = TextInputVisualizer(
    manager=manager, font_object=font, font_color=defaultTextCol, cursor_color=defaultTextCol)

# Set up the screen resolution and colour
displaySurface = pygame.display.set_mode(size, pygame.RESIZABLE)
displaySurface.fill(screenCol)

# Assign the pygame clock to the variable clock
clock = pygame.time.Clock()

# API Stuff
# noinspection SpellCheckingInspection
# apiKey = ""
# openai.api_key = apiKey


def chatgpt(text, name):
    text = "Without greeting me, respond in English as if you are {}. {}".format(name, text)

    # return text  # TESTING CODE

    output = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": text}],
        max_tokens=300
    )

    return output['choices'][0]['message']['content']


def buttons_draw(start, end=99):  # Draws the buttons using the arguments start and end (default of 99)
    z = 0
    for b in buttons:
        z += 1
        if start <= z <= end:
            b.draw()


def menus():  # Displays the current menu layout and handles menu changes
    global inputCategory, msgDisplayed, msgHistory

    # Main Menu
    if buttonMenu.menu:
        titlescreen.display_image()
        buttons_draw(1, 2)

        if buttonHist.menu or buttonCeleb.menu:
            buttonMenu.menu = False
            time.sleep(0.05)

    # Historical Figures Menu
    elif buttonHist.menu:
        buttons_draw(3, 6)
        largeHistImages[screenHist].display_image()
        screenHistText[screenHist].display_text()
        inputCategory = 'Hist'

        if buttonMenu.menu:
            buttonHist.menu = False
            time.sleep(0.05)

    # Present-Day Celebrities Menu
    elif buttonCeleb.menu:
        buttons_draw(3, 6)

        largeCelebImages[screenCeleb].display_image()
        screenCelebText[screenCeleb].display_text()

        inputCategory = 'Celeb'

        if buttonMenu.menu:
            buttonCeleb.menu = False
            time.sleep(0.05)

    # User Input Menu
    elif buttonSel.menu:
        buttons_draw(7)

        if inputCategory == 'Hist':
            smallHistImages[screenHist].display_image()

        if inputCategory == 'Celeb':
            smallCelebImages[screenCeleb].display_image()

        if buttonBack.menu:
            msgDisplayed = []
            msgHistory = []

            buttonSel.menu = False
            time.sleep(0.05)

            if inputCategory == 'Hist':
                buttonHist.menu = True
            if inputCategory == 'Celeb':
                buttonCeleb.menu = True

            buttonBack.menu = False


def choice_buttons():  # Handles the celebrity that the user chooses
    global screenHist, screenCeleb

    # When the Next button is pressed
    if buttonNext.menu:
        if buttonCeleb.menu:
            if screenCeleb < len(largeCelebImages) - 1:
                screenCeleb += 1
            else:
                screenCeleb = 0

        if buttonHist.menu:
            if screenHist < len(largeHistImages) - 1:
                screenHist += 1
            else:
                screenHist = 0

        buttonNext.menu = False

    # When the Prev button is pressed
    if buttonPrev.menu:
        if buttonCeleb.menu:
            if 0 < screenCeleb:
                screenCeleb -= 1
            else:
                screenCeleb = len(largeCelebImages) - 1

        if buttonHist.menu:
            if 0 < screenHist:
                screenHist -= 1
            else:
                screenHist = len(largeHistImages) - 1

        buttonPrev.menu = False


def display_messages():
    # The starting value of y
    y = 25

    for i in msgDisplayed:
        displaySurface.blit(i, (25, y))
        y += msgSpacing


def user_input_screen():  # Handles the user text box and the message history when the Select button is pressed
    global currentCharacter, currentName

    if buttonSel.menu:
        if buttonCeleb.menu:
            buttonCeleb.menu = False
            currentCharacter = screenCelebText[screenCeleb].text
            currentName = celebNames[screenCeleb]

            textinput_custom.cursor_width = 0
            textinput_custom.font_color = (255, 0, 0)

            add_to_history("{}: Hello, I am {}. Ask me some questions!".format(
                currentName, currentCharacter))
            wrap_text("{}: Hello, I am {}. Ask me some questions!".format(
                currentName, currentCharacter))

            textinput_custom.cursor_width = 3
            textinput_custom.font_color = defaultTextCol

        if buttonHist.menu:
            buttonHist.menu = False
            currentCharacter = screenHistText[screenHist].text
            currentName = histNames[screenHist]

            textinput_custom.cursor_width = 0
            textinput_custom.font_color = (255, 0, 0)

            add_to_history("{}: Hello, I am {}. Ask me some questions!".format(
                currentName, currentCharacter))
            wrap_text("{}: Hello, I am {}. Ask me some questions!".format(
                currentName, currentCharacter))

            textinput_custom.cursor_width = 3
            textinput_custom.font_color = defaultTextCol

        # Feed it with events every frame (ensure it fits in the window)
        if textinput_custom.surface.get_width() <= windowDim[0] - msgPadding:
            # The following comment makes sure an inspection error does not appear
            # noinspection PyTypeChecker
            textinput_custom.update(events)
        else:
            maxCharText.display_text()

        display_messages()

        # Displays the user input text box
        displaySurface.blit(textinput_custom.surface, (25, windowDim[1] - 150))


def add_to_history(text):
    # Adds the msg to a list to keep track of the replies ( in case of a resize )
    if len(msgHistory) < msgHistoryMax:
        msgHistory.append(text)
    else:
        msgHistory.pop(0)
        msgHistory.append(text)


def add_msg():
    global msgDisplayedMax

    # noinspection SpellCheckingInspection
    textinput_custom._rerender_required = True

    # The following comment makes sure an inspection error does not appear
    # noinspection PyTypeChecker
    textinput_custom.update(events)

    msgDisplayedMax = (windowDim[1] - 200) // 25

    # Ensure that there is enough space for the new addition to msgDisplayed
    if len(msgDisplayed) < msgDisplayedMax:
        # Add the user text input surface to the list
        msgDisplayed.append(textinput_custom.surface)
    else:  # If there was not enough space for the new message
        # While the list length of msgDisplayed is >= msgDisplayedMax
        while len(msgDisplayed) >= msgDisplayedMax:
            # Delete the first msg saved in the list
            msgDisplayed.pop(0)

        # Add the msg to the list
        msgDisplayed.append(textinput_custom.surface)

    textinput_custom.value = ""

    # The following comment makes sure an inspection error does not appear
    # noinspection PyTypeChecker
    textinput_custom.update(events)


def wrap_text(text):
    # Set the value of the input to nothing
    textinput_custom.value = ""

    # The following comment makes sure an inspection error does not appear
    # noinspection PyTypeChecker
    textinput_custom.update(events)

    # Iterate through all characters
    for c in text:
        # If the text surface is NOT at max size
        if textinput_custom.surface.get_width() <= windowDim[0] - msgPadding:
            # Add the character to the value
            textinput_custom.value += c

        # If the text surface is at max size
        else:
            # Add a "-" to the end
            textinput_custom.value += "-"

            add_msg()

            # If the character is a space, pass
            if c == " ":
                pass

            # If the character is not a space, set the value as the character
            else:
                textinput_custom.value = c

        # noinspection SpellCheckingInspection
        textinput_custom._rerender_required = True

        # The following comment makes sure an inspection error does not appear
        # noinspection PyTypeChecker
        textinput_custom.update(events)

    if not textinput_custom.value.isspace():
        add_msg()


def text_input_output():
    global userInput

    # Stop receiving key inputs
    pygame.key.stop_text_input()

    # If something is typed by the user
    if not (textinput_custom.value.isspace() or textinput_custom.value == ''):
        userInput = textinput_custom.value

        # Add "User: " to the start of the input and set the cursor width to 0px
        textinput_custom.value = "User: " + textinput_custom.value
        textinput_custom.cursor_width = 0

        # Add the msg to msgHistory and wrap the text
        add_to_history(textinput_custom.value)
        wrap_text(textinput_custom.value)

        # Change the text colour to RED and create a random response
        textinput_custom.font_color = (255, 0, 0)
        textinput_custom.value = "{}: ".format(currentName) + chatgpt(userInput, currentCharacter)

        # Add the msg to msgHistory and wrap the text
        add_to_history(textinput_custom.value)
        wrap_text(textinput_custom.value)

    # Change the text colour back to the default colour
    textinput_custom.font_color = defaultTextCol

    # Set the cursor width back to 3px and reset the user's input
    textinput_custom.cursor_width = 3
    textinput_custom.value = ''

    # Resume receiving text inputs
    pygame.key.start_text_input()


def change_button_pos(buttonName, pos=(0, 0)):
    buttonName.original_y_pos = pos[1]
    buttonName.top_rect = pygame.Rect(pos, (buttonName.width, buttonName.height))
    buttonName.bottom_rect = pygame.Rect(pos, (buttonName.width, buttonName.height))


def change_image_pos(imageName, placement="topleft", pos=(0, 0)):
    imageName.kwargs.clear()
    imageName.kwargs.update({placement: pos})
    imageName.set_pos(imageName.kwargs)


def change_text_pos(textName, placement="topleft", pos=(0, 0)):
    textName.kwargs.clear()
    textName.kwargs.update({placement: pos})
    textName.set_pos(textName.kwargs)


def resize_all():
    global maxCharText, msgDisplayed

    # Title Screen
    change_image_pos(titlescreen, "center", (windowDim[0] / 2, windowDim[1] / 2 - 75))

    # Menu Screen Buttons
    change_button_pos(buttonHist, (windowDim[0] / 2 - 365, windowDim[1] - 100))
    change_button_pos(buttonCeleb, (windowDim[0] / 2 - 55, windowDim[1] - 100))

    # Choice Screen Buttons
    change_button_pos(buttonPrev, (windowDim[0] / 2 - 255, windowDim[1] - 100))
    change_button_pos(buttonMenu, (windowDim[0] / 2 - 125, windowDim[1] - 100))
    change_button_pos(buttonSel, (windowDim[0] / 2 + 5, windowDim[1] - 100))
    change_button_pos(buttonNext, (windowDim[0] / 2 + 135, windowDim[1] - 100))

    # User Input Screen Buttons
    change_button_pos(buttonBack, (25, windowDim[1] - 100))

    # Maximum character text for User Input Screen
    maxCharText = Text("MAX CHARACTERS", color=(255, 0, 0), topleft=(windowDim[0] / 2 - 90, windowDim[1] - 82))

    # Large Hist images
    for i in largeHistImages:
        change_image_pos(i, "center", (windowDim[0] / 2, windowDim[1] / 2 - 75))

    # Small Hist images
    for i in smallHistImages:
        change_image_pos(i, "topleft", (155, windowDim[1] - 100))

    # Hist Screen Text
    for i in screenHistText:
        change_text_pos(i, "center", (windowDim[0] / 2, windowDim[1] - 150))

    # Large Celeb images
    for i in largeCelebImages:
        change_image_pos(i, "center", (windowDim[0] / 2, windowDim[1] / 2 - 75))

    # Small Celeb images
    for i in smallCelebImages:
        change_image_pos(i, "topleft", (155, windowDim[1] - 100))

    # Celeb Screen Text
    for i in screenCelebText:
        change_text_pos(i, "center", (windowDim[0] / 2, windowDim[1] - 150))

    # User Input Screen
    msgDisplayed.clear()
    textinput_custom.cursor_width = 0

    if inputCategory == "Hist":
        for i in msgHistory:  # Iterate through all the items in msgHistory
            # Change the colour of the font according to the input

            if i.find("User:") == 0:
                textinput_custom.font_color = defaultTextCol

            for j in histNames:
                if i.find(j) == 0:
                    textinput_custom.font_color = (255, 0, 0)
                    break

            # Wrap the text ( which adds it to msgDisplay )
            wrap_text(i)

    if inputCategory == "Celeb":
        for i in msgHistory:  # Iterate through all the items in msgHistory
            # Change the colour of the font according to the input

            if i.find("User:") == 0:
                textinput_custom.font_color = defaultTextCol

            for j in celebNames:
                if i.find(j) == 0:
                    textinput_custom.font_color = (255, 0, 0)
                    break

            # Wrap the text ( which adds it to msgDisplay )
            wrap_text(i)

    textinput_custom.font_color = defaultTextCol
    textinput_custom.cursor_width = 3


# The game loop
while True:
    # Assign the list of events to events
    events = pygame.event.get()

    # Assign the dimensions of the window to a variable
    windowDim = list((displaySurface.get_width(), displaySurface.get_height()))

    # Sets the fps
    clock.tick(30)

    # Fills the screen with screenCol
    displaySurface.fill(screenCol)

    # Assigns the list of keys pressed to keys; press every 25ms after waiting 300ms
    keys = pygame.key.get_pressed()
    pygame.key.set_repeat(300, 100)

    # Functions that manage / display the GUI
    menus()
    choice_buttons()
    user_input_screen()

    # Assigns the x and y of the mouse to mouse
    mouse = pygame.mouse.get_pos()

    # Sets the caption of the window to the program name
    # noinspection SpellCheckingInspection
    pygame.display.set_caption("Peopl.ai")

    # Goes through each item in events
    for event in events:
        # Code to exit the code if the X button was pressed
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        # If the window gets resized
        if event.type == VIDEORESIZE:
            # Set a minimum size for the window
            if windowDim[1] < 750:
                windowDim[1] = 750

            if windowDim[0] < 750:
                windowDim[0] = 750

            displaySurface = pygame.display.set_mode(windowDim, pygame.RESIZABLE)

            # Reset the users input box and updates
            textinput_custom.value = ''
            # The following comment makes sure an inspection error does not appear
            # noinspection PyTypeChecker
            textinput_custom.update(events)

            resize_all()

        # If a key is pressed and Enter is pressed
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            text_input_output()

        # If the user presses backspace: allow the user's input to be passed
        # NOTE: this code is here to ensure that the user can delete characters after reaching the character limit
        if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
            if textinput_custom.surface.get_width() > windowDim[0] - msgPadding:
                # The following comment makes sure an inspection error does not appear
                # noinspection PyTypeChecker
                textinput_custom.update(events)

    # Updates the display
    pygame.display.update()
