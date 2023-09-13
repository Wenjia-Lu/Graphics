import mdl
from display import *
from matrix import *
from draw import *

def run(filename):
    """
    This function runs an mdl script
    """
    #print(filename)
    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print("Parsing failed.")
        return

    view = [0,
            0,
            1];
    ambient = [50,
               50,
               50]
    light = [[0.5,
              0.75,
              1],
             [255,
              255,
              255]]

    color = [0, 0, 0]
    tmp = new_matrix()
    ident( tmp )

    stack = [ [x[:] for x in tmp] ]
    screen = new_screen()
    zbuffer = new_zbuffer()
    tmp = []
    step_3d = 100
    consts = ''
    coords = []
    coords1 = []
    symbols['.white'] = ['constants',
                         {'red': [0.2, 0.5, 0.5],
                          'green': [0.2, 0.5, 0.5],
                          'blue': [0.2, 0.5, 0.5]}]
    reflect = '.white'

    # VAR INIT
    FRAMES = 1
    BASENAME = 'frame'
    animate = False
    hasFrame = False
    hasVary = False
    hasBase = False
    knobs = []
    symbolTable = []

    with open(filename) as f:
        file = f.read()
        if 'frames' in file and 'vary' in file and 'basename' in file:
            animate=True
        if 'frames' in file:
            hasFrame = True
        if 'vary' in file:
            hasVary = True
        if 'basename' in file:
            hasBase = True

# PASS 0: set frames & basename
# if vary is present but frames is not -> MDL compiler error
# frames present basename not -> print warning, set basename to default val

    for command in commands:
        # print(command)
        c = command['op']
        args = command['args']
        if c == 'frames':

            if not hasBase:
                print("WARNING: no basename command. Initialized basename to 'frame'. ")
                BASENAME = 'frame'

            FRAMES = int(args[0])

            if len(symbolTable) < FRAMES+1:
                symbolTable=[]
                for _ in range(FRAMES+1):
                    symbolTable.append({})
        
        elif c == 'basename':
            BASENAME = args[0]
        
        elif c == 'vary':
# PASS 1: compute knob values for every frame, store in data structure
# make list (each index = 1 frame), each index contain a list of knobs
# vary: compute & add to knob table. (totalchange / frames)

            if not hasFrame:
                raise Exception("MDL COMPILER ERROR: 'frames' count not initialized ")
            
            start_frame = int(args[0])
            end_frame = int(args[1])
            start_val = int(args[2])
            end_val = int(args[3])

            currentVal = start_val
            knobs.append(command['knob'])
            delta = (end_val - start_val) / (end_frame - start_frame)

            for frame in range(start_frame,end_frame+1):
                symbolTable[frame][command['knob']] = currentVal
                currentVal += delta

        elif not animate:
            if c == 'box':
                if command['constants']:
                    reflect = command['constants']
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'sphere':
                if command['constants']:
                    reflect = command['constants']
                add_sphere(tmp,
                        args[0], args[1], args[2], args[3], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'torus':
                if command['constants']:
                    reflect = command['constants']
                add_torus(tmp,
                        args[0], args[1], args[2], args[3], args[4], step_3d)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, zbuffer, view, ambient, light, symbols, reflect)
                tmp = []
                reflect = '.white'
            elif c == 'line':
                add_edge(tmp,
                        args[0], args[1], args[2], args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_lines(tmp, screen, zbuffer, color)
                tmp = []
            elif c == 'move':
                tmp = make_translate(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'scale':
                tmp = make_scale(args[0], args[1], args[2])
                matrix_mult(stack[-1], tmp)
                stack[-1] = [x[:] for x in tmp]
                tmp = []
            elif c == 'rotate':
                theta = args[1] * (math.pi/180)
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])

# frame ==1: runs this
# frame >1: update knob values, plug in knob values,
# save each frame (basename follow by number)
# make a directory of all the img we're saving^
# animate: $ animate basename*
# convert: convert basename* -delay 4.1 basename.gif

    if animate:
        lines = file.split("\n")
        sort = []
        for i in range(len(lines)):
            if not("vary" in lines[i] or "basename" in lines[i] or "frames" in lines[i]):
                sort.append(i)

        for frame in range(FRAMES+1):
            # overwrite
            with open('output.mdl','w') as output:
                output.write("")

            with open('output.mdl','a+') as output:
                for i in sort:
                    line = lines[i]
                    for knob in knobs:
                        if knob in symbolTable[frame]:
                            line = line.replace(knob, str(symbolTable[frame][knob]))
                    output.write(line + "\n")
                output.write("\nsave "+BASENAME+str(frame)+".png")
            run('output.mdl')
