"""
    using from ... import so that we can just type (for example)

        glClearColor(...)

    instead of
        OpenGL.GL.glClearColor(...)
    
    from ... import is useful, but it's a good idea not to use it on every module
    in case two modules have functions with the same name.
"""
from OpenGL.GL import *
# import pygame and give it the nickname pg
import pygame as pg

################################ Initialisation ###############################
pg.init()
"""
    To tell pygame to use opengl, add the option flag pygame.OPENGL
    when starting up screen.

    The second option specifies to use a double buffer system.
    Pygame can run with a single buffer and display.update(), however
    opengl can't, so we'll use a double buffer.

    In general, options are "piped" together with the | operator.
    Under the hood, this is using the concept of bitmasks.

    OPENGL    = 00000010
    DOUBLEBUF = 00000100
    +
    OPENGL | DOUBLEBUF = 000000110
"""
pg.display.set_mode((640,480),pg.OPENGL|pg.DOUBLEBUF)
CLOCK = pg.time.Clock()

"""
    define the colour to use when the screen is refreshed,
    (r,g,b,a)
        r: red [0,1] 0: no red, 1: full red
        g: red [0,1]
        b: red [0,1]
        a: alpha [0,1] 0:transparent, 1: no transparency
    using decimals between 0 and 1 allows for more precision,
    the standard 0-255 system is based on using one byte to represent each colour,
    if more bytes are used then the range gets bigger.

    It's simpler just to use decimals. If bit depth is increased, just let the decimals be more accurate.
"""
glClearColor(0,0.2,0.2,1)

running = True
while running:
    for event in pg.event.get():
        if event.type==pg.QUIT:
            running = False

    # refresh the screen
    glClear(GL_COLOR_BUFFER_BIT)
    # similar to pygame.display.update()
    pg.display.flip()

    # framerate might be interesting as programs get more complex.
    CLOCK.tick()
    framerate = int(CLOCK.get_fps())
    pg.display.set_caption("Running at "+str(framerate)+" frames per second.")

pg.quit()