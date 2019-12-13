import os

with open("day13_input_mod.txt","r") as f:
    prog = f.read().rstrip("\n")
    
class Computer:
    
    def __init__(self, program_string):
        
        self.t = []  # loading program makes this a list of ints
        self.load_program(program_string)
        self.current_pos = 0  # where we are reading memory from, start at 0
        self.func_dict = {}  # mapping of 2-digit opcode to function object
        self.args_dict = {}  # dict of how many args each function expects
        self.load_functions()
        self.input = []
        self.output = []  # queues of values written in or out
        self.gen = self.make_generator()  # the generator object that runs the code
        self.halted = False   # check from outside if program is complete
        self.relative_base = 0  # introduced day 9
        self.waiting_for_input = False

    
    def load_program(self, strin):
        
        '''Loads in a comma delimited program string and sets up memory'''
        
        self.t = [int(x) for x in strin.split(",")] + [0 for _ in range(10000)]
        
    def load_functions(self):
        
        for x in dir(self):
            obj = getattr(self, x)
            doc = obj.__doc__
            if doc and len(doc) == 2:
                # it's an opcode function
                self.func_dict[doc] = obj
                if obj.__defaults__:
                    self.args_dict[doc] = len(obj.__defaults__)
                else:
                    self.args_dict[doc] = 0  # function expects no args
        # now we can look up functions by the opcode 2-character STRING

        
    ### Opcode function definitions, these are loaded by 
    ### introspection into a dict ###
    # a memory destination argument has a default of "dest" so that
    # the argument dispatcher can detect it's a memory address
    
    def add(self, a=None, b=None, dest="dest"):
        '''01'''
        self.t[dest] = a + b
        
    def multiply(self, a=None, b=None, dest="dest"):
        '''02'''
        self.t[dest] = a * b
        
    def get_input(self, dest="dest"):
        '''03'''
        # consumes one value from the input queue and writes it to memory
        if len(self.input) > 0:
            val = self.input.pop(0)  # FIFO queue
            self.t[dest] = val
        else:
            return "WAIT_FOR_INPUT"  # this causes the evaluation generator to yield
        
    def send_output(self, a=None):
        '''04'''
        # reads a value from memory and writes it to the output queue
        #print(f"outputting {self.t[dest]}")
        #self.output.append(self.t[a])
        self.output.append(a)
        
    def jump_if_true(self, a=None, b=None):   # changed b=dest to none
        '''05'''
        if not a == 0:
            self.current_pos = b
        else:
            self.current_pos += 3
            
    def jump_if_false(self, a=None, b=None):
        '''06'''
        if a == 0:
            self.current_pos = b
        else:
            self.current_pos += 3
            
    def less_than(self, a=None, b=None, dest="dest"):
        '''07'''
        if a < b:
            self.t[dest] = 1
        else:
            self.t[dest] = 0
            
    def equals(self, a=None, b=None, dest="dest"):
        '''08'''
        if a == b:
            self.t[dest] = 1
        else:
            self.t[dest] = 0
            
    def relative_base_offset(self, a=None):
        '''09'''
        self.relative_base += a
            
    def halt(self):
        '''99'''
        self.halted = True
        return "HALT"  # breaks out of the execution loop
    
    def prepare_args(self, func, modes, args):
        
        '''recieves a reference to func so it can determine whether
        its last argument is a memory address'''
        
        out = []
        if func.__defaults__:
            q = zip(modes, args, func.__defaults__)
            # an iterator to provide values in the loop
        else:
            return []  # func takes no arguments
        

        while True:
                
            try:
                m, a, default = next(q) # get the next mode and argument
            except StopIteration:  # never encountered a final argument "dest"
                break
            #print(m, a, default)
            if default == "dest":
                if m == "2":
                    out.append(self.relative_base + a)
                else:
                    out.append(a)
                break  # the last argument is always a memory address to write to
                # zfill might make this appear as mode 0, but it's always
                # effectively mode 1 by default, or can be 2 also
            if m == "0":  # positional mode
                out.append(self.t[a])
            elif m == "1": # immediate mode
                out.append(a)
            elif m == "2":  # relative mode
                out.append(self.t[self.relative_base + a])
        
        return out
    
    def make_generator(self):
        
        def gen():
            '''the actual object that runs the code'''
            
            while True:

                self.waiting_for_input = False
                tmp = self.current_pos  # store to see if a jump happened, if so,
                # we don't need to advance the memory
                opcode = str(self.t[self.current_pos]).zfill(2)
                instruction = opcode[-2:]  # look up the instruction
                modes = opcode[:-2]  # up to and including third from the end
                required_args = self.args_dict[instruction]  # how many args
                
                modes = modes.zfill(required_args)
                modes = modes[::-1]
                arg_addrs = self.t[self.current_pos+1:self.current_pos+1+required_args]
                func = self.func_dict[instruction]
                #print(f"preparing args for {func} with modes {modes}")                
                args = self.prepare_args(func, modes, arg_addrs)
                
                # UNCOMMENT FOR DEBUGGING
                #print(f"Running {func.__name__} with args {args} in modes {modes}")
                
                z = func(*args)  # evaluate the function, check for return
                
                if z == "HALT":
                    #print("halting in while loop")
                    break  # opcode 99
                elif z == "WAIT_FOR_INPUT":
                    #print(f"Computer {self} is waiting for input")
                    self.waiting_for_input = True
                    yield
                    continue  # want to re-run the input instruction, not advance
                if tmp == self.current_pos:  # the current_pos has not been altered
                    self.current_pos += required_args + 1
                else:
                    pass
                    # a jump instruction has moved the current position
                    # so we don't need to advance it ourselves
                
            #print("before final while return statement")
            return
        
        return gen()
    
    def run(self):
        
        if self.halted:
            return False  # to send the signal that program is finished
        try:
            a = next(self.gen)
        except StopIteration:
            pass
            print(f"Computer {self} has halted")
        if len(self.output) > 0:
            pass
            # return self.output.pop()
        
    def send_input(self, value):
        
        self.input.append(value)

        
class Arcade(Computer):
    
    """some methods overridden to interface with the screen and inputs"""
    
    def __init__(self, prog, screen):
        
        super().__init__(prog)
        self.screen = screen  # reference to the screen array
    
    def send_output(self, a=None):
        '''04'''
        self.output.append(a)
        if len(self.output) == 3:
            if a == -1 and b == 0:
                print(c)
            else:
                a, b, c = self.output
                self.screen.drawfunc(a, b, c)
            self.output.clear()

            
class Screen:
    
    def __init__(self):
        
        self.array = [[0 for a in range(100)] for b in range(100)]
        self.id_dict = {0:".", 1:"W", 2:"X", 3:"=", 4:"O"}
        self.drawfunc = self.first_draw
        self.ball_y = 0
        self.paddle_y = 0
        self.score = 0
        
    def start_drawing(self):
    
        self.drawfunc = self.draw  # re-bind function to start rendering screen
        
    def first_draw(self, a, b, c):
    
        """non-refreshing function for initial setup"""
        
        self.update_array(a, b, c)
        
    def draw(self, a, b, c):
        
        self.update_array(a, b, c)
        self.refresh()
        
    def update_array(self, a, b, c):
    
        try:
            self.array[b][a] = self.id_dict[c]
            if c == 4:
                self.ball_y = a
            elif c == 3:
                self.paddle_y = a
            
        except KeyError:
            y = 0
            for char in str(c):
                self.array[0][y] = char
                y += 1
            self.score = c
        
    def refresh(self):
        
        os.system("cls")
        
        out = ""
        
        for x in self.array[:24]:
            for y in x[:38]:
                out += str(y)
            out += "\n"
        
        print(out)
        
        
def run():
    
    cnt = 0
    s = Screen()
    c = Arcade(prog, s)
    out = []
    while not c.halted:
        c.run()
        if cnt > 24*37:  # initial drawing of the screen
            # s.start_drawing()  # uncomment to see the game on the screen
            if s.ball_y > s.paddle_y:  # always keep the paddle under the ball
                b = "d"
            elif s.ball_y < s.paddle_y:
                b = "a"
            else:
                b = None

            if b == "d":
                c.send_input(1)
            elif b == "a":
                c.send_input(-1)
            else:
                c.send_input(0)

        cnt += 1

    print(s.score)
    
result = run()