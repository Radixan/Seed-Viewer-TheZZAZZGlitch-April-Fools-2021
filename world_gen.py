world_seed = bytearray([0x00, 0x00, 0x00, 0x00])
current_seed = world_seed.copy()
MAP_SIZE = 0x08
mem_map = bytearray([0x0F] * (MAP_SIZE * MAP_SIZE))

CONNECTION_TABLE = b'\x05\x0B\x06\x00\x0E\x05\x0B\x03\x09\x0E\x00\x00\x00\x0C\x00\x00\x00\x0C\x05\x06\x06\x0D\x0A\x09\x09\x0B\x06\x00\x00\x05\x0A\x00\x05\x0B\x06\x00\x0B\x06\x09\x07\x00\x09\x07\x0A\x00\x05\x0A\x00\x00\x09\x06\x00\x03\x06\x0C\x05\x00\x09\x0F\x0A\x00\x05\x0A\x00\x05\x0A\x00\x00\x0F\x06\x05\x03\x09\x0F\x0A\x00\x00\x0C\x00\x00\x05\x0B\x03\x06\x0E\x00\x00\x0D\x09\x06\x00\x0C\x00\x0D\x03\x0A\x00\x09\x06\x00\x06\x05\x0A\x05\x09\x0F\x06\x0C\x00\x0C\x09\x0A\x00\x0C\x00\x00\x03\x0F\x07\x03\x00\x0D\x0A\x00\x00\x0C\x00\x00'

NONE = 0x00

TREES = 0x0F
TREES_UP = 0x6C
TREES_DOWN = 0x6F
TREES_LEFT = 0x6E
TREES_RIGHT = 0x6D

GRASS = 0x0A
GRASSIER = 0x7A
GRASSIEST = 0x7B
MEGA_GRASS = 0x31
TALL_GRASS = 0x0B
FLOWER = 0x74

POKE_UP = 0x33
POKE_RIGHT = 0x32
POKE_LEFT = 0x60
POKE_DOWN = 0x34
POKE_GRASS = 0x08

ROAD = 0x55
BARRIER = 0x13
BARRIER_UP = 0x4E
BARRIER_DOWN = 0x4D
BARRIER_LEFT = 0x51
BARRIER_RIGHT = 0x52

GLITCH_C9 = 0xC9
GLITCH_CA = 0xCA
GLITCH_CB = 0xCB
GLITCH_D9 = 0xD9
GLITCH_DB = 0xDB
GLITCH_EC = 0xEC

XY_UP = (4, 0)
XY_LEFT = (0, 4)
XY_DOWN = (4, 7)
XY_RIGHT = (7, 4)
XY_CENTER = (4, 4)

def xytoi(xy): return xy[0] + xy[1] * MAP_SIZE

INDEX_UP    = xytoi(XY_UP)
INDEX_LEFT  = xytoi(XY_LEFT)
INDEX_DOWN  = xytoi(XY_DOWN)
INDEX_RIGHT = xytoi(XY_RIGHT)
INDEX_CENTER = xytoi(XY_CENTER)

def next_random(): #A850
   global current_seed
   current_seed[0] = (current_seed[0] + 1) & 0xFF
   current_seed[1] ^= current_seed[3] ^ current_seed[0] 
   current_seed[2] = (current_seed[2] + current_seed[1]) & 0xFF
   current_seed[3] = (current_seed[3] + ((current_seed[2] >> 1) ^ current_seed[1])) & 0xFF
   return current_seed[3]

def generate_chunk_seed(x, y): #A878
    global current_seed, world_seed
    current_seed[0] = world_seed[0] ^ (x >> 0x08)
    current_seed[1] = world_seed[1] ^ (x &  0xff)
    current_seed[2] = world_seed[2] ^ (y >> 0x08)
    current_seed[3] = world_seed[3] ^ (y &  0xff)
    for _ in range(16):
       next_random()

def get_biome_and_connections(x, y): #A896
   generate_chunk_seed(x & 0xfffc, y & 0xfffc)
   
   connections = CONNECTION_TABLE[(x & 0x03) + (y & 0x03) * 4 + ((next_random() & 0x07) << 4)]
   biome = ((next_random() & 0x30) >> 4) * ((x | y) & 0xfffc != 0)
   
   return (biome, connections)

def expand_block(block): #A998
   mem_cpy = mem_map.copy()
   
   for i in range(MAP_SIZE, (MAP_SIZE - 1) * MAP_SIZE):
      if block != mem_cpy[i] or not 7 > (i & 0x7) > 0: continue
      direction = next_random()
      if direction & 1: mem_map[i - 1] = block
      if direction & 2: mem_map[i + 1] = block
      if direction & 4: mem_map[i - MAP_SIZE] = block
      if direction & 8: mem_map[i + MAP_SIZE] = block

def traceline(x1, y1, x2, y2, block): #A907
   xi = 1 - ((x2 < x1) << 1)
   yi = 1 - ((y2 < y1) << 1)
   mem_map[x1 + y1 * MAP_SIZE] = block
   
   while x1 != x2 or y1 != y2:
      if x1 != x2: x1 += xi
      mem_map[x1 + y1 * MAP_SIZE] = block
      if y1 != y2: y1 += yi
      mem_map[x1 + y1 * MAP_SIZE] = block

def traceline_through_random(x1, y1, x2, y2, block): #A8DF
   while (x := next_random() & 0x07) == 0x00 or x == 0x07: pass
   while (y := next_random() & 0x07) == 0x00 or y == 0x07: pass
   
   traceline(x1, y1, x, y, block)
   traceline(x, y, x2, y2, block)

def replace_with_chance(prob, src, dst): #A9DC
   for i in range(MAP_SIZE * MAP_SIZE):
      if mem_map[i] != src or next_random() >= prob: continue
      mem_map[i] = dst

def replace_with_chance_inner(prob, src, dst): #A9F8
   for it in range(MAP_SIZE, (MAP_SIZE - 1) * MAP_SIZE):
      if mem_map[it] != src or not 7 > (it & 7) > 0 or next_random() >= prob: continue
      mem_map[it] = dst

def replace_with_chance_and_neighborship(prob, src, dest, up, dw, lf, rg): #AA14
   for it in range(MAP_SIZE, (MAP_SIZE - 1) * MAP_SIZE):
      if mem_map[it] != src or not 7 > (it & 0x07) > 0 or next_random() < prob or \
         up and mem_map[it - MAP_SIZE] != up or dw and mem_map[it + MAP_SIZE] != dw or \
         lf and mem_map[it - 1] != lf or rg and mem_map[it + 1] != rg: continue
      
      mem_map[it] = dest

def grasslands_generator(entry, connections): # ABCE
   replace_with_chance(48, GRASS, TALL_GRASS)
   expand_block(TALL_GRASS)
   
   replace_with_chance_and_neighborship(32, TREES, TREES_UP   , TREES, GRASS, NONE , NONE )
   replace_with_chance_and_neighborship(32, TREES, TREES_DOWN , GRASS, TREES, NONE , NONE )
   replace_with_chance_and_neighborship(32, TREES, TREES_LEFT , NONE , NONE , GRASS, TREES)
   replace_with_chance_and_neighborship(32, TREES, TREES_RIGHT, NONE , NONE , TREES, GRASS)
   
   replace_with_chance(48, GRASS, FLOWER)
   replace_with_chance(48, GRASS, GRASSIER)
   
   replace_with_chance_inner(64, TREES_UP   , POKE_UP)
   replace_with_chance_inner(64, TREES_RIGHT, POKE_RIGHT)
   replace_with_chance_inner(64, TREES_LEFT , POKE_LEFT)
   replace_with_chance_inner(64, TREES_DOWN , POKE_DOWN)

def construct_generator(entry, connections): # AC71
   replace_with_chance_and_neighborship(192, TREES, BARRIER, NONE, NONE, NONE, GRASS)
   replace_with_chance_and_neighborship(192, TREES, BARRIER, NONE, NONE, GRASS, NONE)
   
   replace_with_chance_and_neighborship( 96, GRASS, BARRIER_LEFT , NONE , NONE , TREES, NONE )
   replace_with_chance_and_neighborship( 96, GRASS, BARRIER_RIGHT, NONE , NONE , NONE , TREES)
   replace_with_chance_and_neighborship( 96, GRASS, BARRIER_UP   , TREES, NONE , NONE , NONE )
   replace_with_chance_and_neighborship( 96, GRASS, BARRIER_DOWN , NONE , TREES, NONE , NONE )
      
   if connections & 8: traceline(*entry, *XY_UP, ROAD)
   if connections & 4: traceline(*entry, *XY_DOWN, ROAD)
   if connections & 2: traceline(*entry, *XY_LEFT, ROAD)
   if connections & 1: traceline(*entry, *XY_RIGHT, ROAD)
   
   replace_with_chance(80, GRASS, TALL_GRASS)
   replace_with_chance(192, GRASS, GRASSIER)
   replace_with_chance(116, GRASS, TALL_GRASS)
   
   replace_with_chance_inner(24, BARRIER_LEFT, POKE_RIGHT)
   replace_with_chance_inner(24, BARRIER_RIGHT, POKE_LEFT)
   
def steppes_generator(entry, connections): #AC51
   replace_with_chance(64, GRASS, GRASSIEST)
   replace_with_chance(48, GRASS, GRASSIER)
   replace_with_chance(208, GRASS, TALL_GRASS)
   replace_with_chance_inner(32, GRASS, POKE_GRASS)

GLITCH_BLOCKS = [GLITCH_D9, GLITCH_DB, GLITCH_CA, GLITCH_CB] #ADD9:ADDC
def corruption_generator(entry, connections): #AD24
   global mem_map
   replace_with_chance_and_neighborship(64, TREES, GLITCH_EC, NONE , NONE , GRASS, NONE )
   replace_with_chance_and_neighborship(64, TREES, GLITCH_EC, NONE , NONE , NONE , GRASS)
   replace_with_chance_and_neighborship(64, TREES, GLITCH_EC, GRASS, NONE , NONE , NONE )   
   replace_with_chance_and_neighborship(64, TREES, GLITCH_EC, NONE , GRASS, NONE , NONE )
   
   replace_with_chance(128, GLITCH_EC, GLITCH_C9)
   replace_with_chance(128, GRASS, TALL_GRASS)
   for i in range(MAP_SIZE * MAP_SIZE):
      if mem_map[i] != TREES or next_random() >= 64: continue
      mem_map[i] = GLITCH_BLOCKS[next_random() & 0x03]
   
   if connections & 8: traceline(*entry, *XY_UP, MEGA_GRASS)
   if connections & 4: traceline(*entry, *XY_DOWN, MEGA_GRASS)
   if connections & 2: traceline(*entry, *XY_LEFT, MEGA_GRASS)
   if connections & 1: traceline(*entry, *XY_RIGHT, MEGA_GRASS)
   
   replace_with_chance(32, MEGA_GRASS, TALL_GRASS)
   replace_with_chance_inner(16, MEGA_GRASS, POKE_GRASS)

#             ABCE                  AC51               AC71                 AD24
GENERATORS = [grasslands_generator, steppes_generator, construct_generator, corruption_generator]

def generate_chunk(x, y): #AA87
    global mem_map
    biome, connections = get_biome_and_connections(x,y)
    mem_map = bytearray([0x0F] * (MAP_SIZE * MAP_SIZE))

    entry = None
    
    if connections & 1: entry = XY_RIGHT
    if connections & 2: entry = XY_LEFT
    if connections & 4: entry = XY_DOWN
    if connections & 8: entry = XY_UP
    
    generate_chunk_seed(x, y)
    
    if connections & 1: traceline_through_random(*entry, *XY_RIGHT, GRASS)
    if connections & 2: traceline_through_random(*entry, *XY_LEFT, GRASS)
    if connections & 4: traceline_through_random(*entry, *XY_DOWN, GRASS)
    if connections & 8: traceline_through_random(*entry, *XY_UP, GRASS)
    
    expand_block(GRASS)
    
    if connections & 8:
       mem_map[INDEX_UP - 1] = GRASS
       mem_map[INDEX_UP] = GRASS
    if connections & 4:
       mem_map[INDEX_DOWN - 1] = GRASS
       mem_map[INDEX_DOWN] = GRASS
    if connections & 2:
       mem_map[INDEX_LEFT - MAP_SIZE] = GRASS
       mem_map[INDEX_LEFT] = GRASS
    if connections & 1:
       mem_map[INDEX_RIGHT - MAP_SIZE] = GRASS
       mem_map[INDEX_RIGHT] = GRASS
    
    GENERATORS[biome](entry, connections)
    return mem_map

def find_spawn():
   for i, t in enumerate(mem_map):
      if t == GRASS:
         return i
   return INDEX_CENTER
