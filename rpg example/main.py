import pygame
import pathlib

############################### Model   #######################################

class Player:
    pass

class Tree:
    pass

class GameWorld:
    pass

############################### View    #######################################

class GenericGraphicsObject:
    def __init__(self):
        self.can_click = False
        self.depth = 0
    
    def draw(self):
        pass

class Rectangle(GenericGraphicsObject):
    def __init__(self,left,top,width,height,game,**kwargs):
        super().__init__()
        self.rect = pygame.Rect(left,top,width,height)
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.game = game
        if 'colour' in kwargs:
            self.colour = kwargs['colour']
        if 'border' in kwargs:
            self.border = kwargs['border']
        else:
            self.border = 0
        if 'depth' in kwargs:
            self.depth = kwargs['depth']
    
    def mouse_inside(self):
        (x,y) = pygame.mouse.get_pos()
        return (x>self.left and y>self.top and x<(self.left+self.width) and y<(self.top+self.height))
    
    def update(self):
        pass

    def draw(self):
        pygame.draw.rect(self.game.screen,self.colour,self.rect,self.border)

class Button(GenericGraphicsObject):
    def __init__(self, left, top, width, height, game, **kwargs):
        super().__init__()
        self.highlighted = False
        self.text = ''
        self.rect = pygame.Rect(left,top,width,height)
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.game = game
        if 'colour' in kwargs:
            self.colour_original = kwargs['colour']
        if 'text_colour' in kwargs:
            self.text_colour_original = kwargs['text_colour']
        if 'depth' in kwargs:
            self.depth = kwargs['depth']
        if 'text' in kwargs:
            self.text = kwargs['text']
        if 'image' in kwargs:
            self.image = pygame.image.load(kwargs['image'])
        else:
            self.image = None
    
    def set_click_action(self, function):
        self.can_click = True
        self.click_action = function

    def mouse_inside(self):
        (x,y) = pygame.mouse.get_pos()
        return (x>self.left and y>self.top and x<(self.left+self.width) and y<(self.top+self.height))

    def update(self):
        if self.mouse_inside() or self.highlighted:
            self.colour = self.text_colour_original
            self.text_colour = self.colour_original
        else:
            self.colour = self.colour_original
            self.text_colour = self.text_colour_original

    def draw(self):

        pygame.draw.rect(self.game.screen,self.colour,self.rect)
        if self.text:
            text = self.game.font.render(self.text,True,self.text_colour)
            self.game.screen.blit(text,self.rect.move(10,10))
        if self.image:
            self.game.screen.blit(self.image,self.rect)
        
class View:
    def __init__(self):
        #queue of draw instructions
        self.graphics_objects = []
    
    def insert_graphics_object(self,obj):
        insertion_point = 0
        for go in self.graphics_objects:
            if obj.depth > go.depth:
                break
            else:
                insertion_point += 1

        self.graphics_objects.insert(insertion_point,obj)
    
    def draw_queue(self):
        while len(self.graphics_objects)>0:
            self.graphics_objects.pop(0).draw()

############################### Control #######################################

class App:
    def __init__(self):
        pygame.init()
        self.screen_dimensions = (640,480)
        self.screen = pygame.display.set_mode(self.screen_dimensions)
        self.colours = {'black': (0,0,0), 'blue': (0,0,255), 'green': (0,255,0),
                        'red': (255,0,0), 'cyan': (0,255,255), 'yellow': (255,255,0),
                        'white': (255,255,255)}
        self.font = pygame.font.SysFont('comic sans',36)

        self.view = View()
        self.state = "start"
        self.control_objects = []
        self.control_objects.append(StartMenu(self))
        self.game_loop()
        pygame.quit()
    
    def game_loop(self):
        running = True
        while running:
            #events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                for co in self.control_objects:
                    if co.type==self.state:
                        co.handle_event(event)
            
            #update
            for co in self.control_objects:
                if co.type==self.state:
                    co.update()

            #draw
            for co in self.control_objects:
                if co.type==self.state:
                    for c in co.components:
                        self.view.insert_graphics_object(c)
            self.view.draw_queue()
            pygame.display.update()

class StartMenu:
    def __init__(self,parent):
        self.type = "start"
        self.components = []
        self.parent = parent

        level_select = Button(240,360,160,60,parent,depth=0,text="Select Level",colour=parent.colours['yellow'],text_colour=parent.colours['blue'])
        level_select.set_click_action(self.select_clicked)
        self.components.append(level_select)

        background = Rectangle(0,0,parent.screen_dimensions[0],parent.screen_dimensions[1],parent,depth=1,colour=parent.colours['red'])
        self.components.append(background)

    def update(self):
        for c in self.components:
            c.update()
    
    def handle_event(self,event):
        if event.type==pygame.MOUSEBUTTONDOWN:
            for c in self.components:
                if c.mouse_inside() and c.can_click:
                    c.click_action()

    def select_clicked(self):
        self.parent.control_objects.pop(self.parent.control_objects.index(self))
        self.parent.control_objects.append(LevelSelectMenu(self.parent))
        self.parent.state = "load"

class LevelSelectMenu:
    def __init__(self,parent):
        self.type = "load"
        self.components = []
        self.parent = parent
        
        self.level_count = 0
        self.first_visible_level = 0
        self.max_visible_levels = 7
        self.last_visible_level = 0
        self.currently_selected_level = None
        self.level_names = []
        self.file_entries = []

        self.browseFolder()
        
        for i in range(self.last_visible_level-self.first_visible_level+1):
            label = self.level_names[i][7:-5]
            entry = Button(102,56+34*i,316,34,parent,depth=0,text=label,colour=parent.colours['cyan'],text_colour=parent.colours['blue'])
            entry.set_click_action(self.entry_clicked)
            self.components.append(entry)
            self.file_entries.append(entry)

        up = Button(450,50,32,32,parent,depth=0,colour=parent.colours['cyan'],text_colour=parent.colours['blue'],image="gfx/up.png")
        up.set_click_action(self.up_clicked)
        self.components.append(up)

        down = Button(450,300-32,32,32,parent,depth=0,colour=parent.colours['cyan'],text_colour=parent.colours['blue'],image="gfx/down.png")
        down.set_click_action(self.down_clicked)
        self.components.append(down)

        background = Rectangle(0,0,parent.screen_dimensions[0],parent.screen_dimensions[1],parent,depth=2,colour=parent.colours['red'])
        self.components.append(background)

        file_window = Rectangle(100,50,320,250,parent,depth=1,colour=parent.colours['blue'])
        self.components.append(file_window)

        play_button = Button(240,360,160,60,parent,depth=0,text="Play",colour=parent.colours['yellow'],text_colour=parent.colours['blue'])
        play_button.set_click_action(self.play_clicked)
        self.components.append(play_button)

    def down_clicked(self,entry):
        entry_to_remove = self.file_entries[0]
        self.file_entries.pop(0)
        self.components.pop(self.components.index(entry_to_remove))

        self.first_visible_level += 1
        if self.first_visible_level >= self.level_count:
            self.first_visible_level -= self.level_count
        self.last_visible_level += 1
        if self.last_visible_level >= self.level_count:
            self.last_visible_level -= self.level_count
        
        for entry in self.file_entries:
            entry.top -= 34
            entry.rect.move_ip(0,-34)

        label = self.level_names[self.last_visible_level][7:-5]
        entry_to_add = Button(102,56+34*6,316,34,self.parent,depth=0,text=label,colour=self.parent.colours['cyan'],text_colour=self.parent.colours['blue'])
        entry_to_add.set_click_action(self.entry_clicked)
        self.file_entries.append(entry_to_add)
        self.components.append(entry_to_add)

    def up_clicked(self,entry):
        for entry in self.file_entries:
            entry.top += 34
            entry.rect.move_ip(0,34)

        self.first_visible_level -= 1
        if self.first_visible_level < 0:
            self.first_visible_level += self.level_count
        self.last_visible_level -= 1
        if self.last_visible_level < 0:
            self.last_visible_level += self.level_count
        
        label = self.level_names[self.first_visible_level][7:-5]
        entry_to_add = Button(102,56,316,34,self.parent,depth=0,text=label,colour=self.parent.colours['cyan'],text_colour=self.parent.colours['blue'])
        entry_to_add.set_click_action(self.entry_clicked)
        self.file_entries.insert(0,entry_to_add)
        self.components.append(entry_to_add)

        entry_to_remove = self.file_entries.pop()
        self.components.pop(self.components.index(entry_to_remove))

    def browseFolder(self):
        for path in pathlib.Path("levels/").iterdir():
            if path.is_file():
                if str(path).rsplit('.')[-1]=='json':
                    self.level_names.append(str(path))
                    self.level_count += 1

        if len(self.level_names)>=0:
            self.first_visible_level = 0
            self.last_visible_level = min(len(self.level_names)-1,self.max_visible_levels-1)

    def update(self):
        for c in self.components:
            c.update()
    
    def handle_event(self,event):
        if event.type==pygame.MOUSEBUTTONDOWN:
            for c in self.components:
                if c.mouse_inside() and c.can_click:
                    c.click_action(c)

    def play_clicked(self,entry):
        if self.currently_selected_level==None:
            return
        else:
            print(f'let\'s play {self.currently_selected_level.text} !')
    
    def entry_clicked(self,entry):
        if self.currently_selected_level != None:
            self.currently_selected_level.highlighted = False
        self.currently_selected_level = entry
        entry.highlighted = True
        
def main():
    app = App()

main()