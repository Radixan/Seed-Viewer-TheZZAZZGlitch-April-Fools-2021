import world_gen as wg
from world_gen import *
import pygame
import math
import sys

TILE_SIZE = 32
TEXTURE_UNKNOWN = pygame.image.load("resources/unknown.bmp")
textures = {
   TREES      : pygame.image.load("resources/trees.bmp"),
   TREES_UP   : pygame.image.load("resources/trees_up.bmp"),
   TREES_DOWN : pygame.image.load("resources/trees_down.bmp"),
   TREES_LEFT : pygame.image.load("resources/trees_right.bmp"),
   TREES_RIGHT: pygame.image.load("resources/trees_left.bmp"),
   
   POKE_UP    : pygame.image.load("resources/poke_up.bmp"),
   POKE_DOWN  : pygame.image.load("resources/poke_down.bmp"),
   POKE_LEFT  : pygame.image.load("resources/poke_right.bmp"),
   POKE_RIGHT : pygame.image.load("resources/poke_left.bmp"),
   POKE_GRASS : pygame.image.load("resources/poke_grass.bmp"),
   
   GRASS      : pygame.image.load("resources/grass.bmp"),
   GRASSIER   : pygame.image.load("resources/grassier.bmp"),
   GRASSIEST  : pygame.image.load("resources/grassiest.bmp"),
   MEGA_GRASS : pygame.image.load("resources/mega_grass.bmp"),
   TALL_GRASS : pygame.image.load("resources/tall_grass.bmp"),
   FLOWER     : pygame.image.load("resources/flowers.bmp"),
   
   ROAD       : pygame.image.load("resources/road.bmp"),
   BARRIER    : pygame.image.load("resources/barrier.bmp"),
   BARRIER_UP   : pygame.image.load("resources/barrier_up.bmp"),
   BARRIER_DOWN : pygame.image.load("resources/barrier_down.bmp"),
   BARRIER_LEFT : pygame.image.load("resources/barrier_left.bmp"),
   BARRIER_RIGHT: pygame.image.load("resources/barrier_right.bmp"),
   
   GLITCH_C9  : pygame.image.load("resources/glitch_C9.bmp"),
   GLITCH_CA  : pygame.image.load("resources/glitch_CA.bmp"),
   GLITCH_CB  : pygame.image.load("resources/glitch_CB.bmp"),
   GLITCH_D9  : pygame.image.load("resources/glitch_D9.bmp"),
   GLITCH_DB  : pygame.image.load("resources/glitch_DB.bmp"),
   GLITCH_EC  : pygame.image.load("resources/glitch_EC.bmp"),
   
   '0_PLAYER': pygame.image.load("resources/player.png"),
   '16_PTR': pygame.image.load("resources/ptr.png")
}
   
PALETTES = (((24, 16, 16, 255), (165, 214, 255, 255), (173, 231,  90, 255), (255, 239, 255, 255)), # grasslands
            ((24, 16, 16, 255), (165, 214, 255, 255), (189, 206, 132, 255), (255, 239, 255, 255)), # steppes
            ((24, 16, 16, 255), (165, 214, 255, 255), (222, 222,  24, 255), (255, 239, 255, 255)), # construct
            ((24, 16, 16, 255), (165, 214, 255, 255), (222, 165, 222, 255), (255, 239, 255, 255))) # corruption
   
class Path:
   def __init__(self, _type = 0, color = (0, 0, 0), points = []):
      self.type = _type
      self.color = color
      self.points = points

def text_with_shadow(x, y, s, a, b):
   screen.blit(b, (x        , y        ))
   screen.blit(b, (x + s    , y        ))
   screen.blit(b, (x + s + s, y        ))
   screen.blit(b, (x + s + s, y + s    ))
   screen.blit(b, (x + s + s, y + s + s))
   screen.blit(b, (x + s    , y + s + s))
   screen.blit(b, (x        , y + s + s))
   screen.blit(a, (x + s    , y + s    ))
   
def end_edit_seed(ignore = False):
   global writing_seed, new_seed, seed_texture, seed_shadow, old_seed_texture, old_seed_shadow, maps, map_textures, spawn
   writing_seed = False
   if not ignore and new_seed != wg.world_seed:
      old_seed_texture = seed_shadow
      old_seed_shadow = seed_texture
      
      wg.world_seed = new_seed
      curr_map = generate_chunk(1, 2)
      spawn = find_spawn()
      maps = {(1,2): curr_map}
      map_textures = {}
   
   seed_texture = old_seed_texture
   seed_shadow = old_seed_shadow

def start_edit_seed():
   global writing_seed, new_seed, seed_texture, seed_shadow
   writing_seed = True
   new_seed = wg.world_seed.copy()
   old_seed_texture = seed_texture
   old_seed_shadow = seed_shadow
   seed_shadow = old_seed_texture
   seed_texture = old_seed_shadow

def update_seed_textures(seed = wg.world_seed, invert = False):
   global seed_texture, seed_shadow
   seed_texture = ''.join([f'{i:02X}' for i in seed])
   seed_shadow = font.render(seed_texture, False, (0, 0, 0))
   seed_texture = font.render(seed_texture, False, (255, 255, 255))
   if invert:
      aux = seed_texture
      seed_texture = seed_shadow
      seed_shadow = aux
   seed_shadow = pygame.transform.scale(seed_shadow, (seed_shadow.get_width() * 2, seed_shadow.get_height() * 2))
   seed_texture = pygame.transform.scale(seed_texture, (seed_texture.get_width() * 2, seed_texture.get_height() * 2))

def ambishift(n, m):
   return n << m if m >= 0 else n >> -m


if __name__ == '__main__':
   try: it = int(sys.argv[1], 16)
   except: it = 0x00
   wg.world_seed = bytearray(it.to_bytes(4, 'big'))
   
   curr_map = generate_chunk(1, 2)
   spawn = find_spawn()
   
   scr_size = (800, 600)
   screen = pygame.display.set_mode(scr_size, pygame.RESIZABLE)
   pygame.display.set_caption('Seed Viewer - TheZZAZZGlitch April Fools 2021')
   pygame.display.set_icon(textures['16_PTR'])
   clock = pygame.time.Clock()
   
   run = True
   drag = False
   last_click = 0

   xpos = int(1.5 * TILE_SIZE * MAP_SIZE)
   ypos = int(2.5 * TILE_SIZE * MAP_SIZE)

   zoom = 0
   
   render_size = TILE_SIZE
   rmapsize = MAP_SIZE * render_size

   map_cx = math.ceil(scr_size[0] / rmapsize)
   map_cy = math.ceil(scr_size[1] / rmapsize)
   maps = {(1,2): curr_map}
   map_textures = {}
   
   pygame.font.init()
   font = pygame.font.Font('resources/pkm-font.ttf', 8)

   pathing = 0
   paths = []
   
   writing_seed = False
   new_seed = None
   
   seed_texture = None
   seed_shadow = None
   update_seed_textures(wg.world_seed)
   old_seed_texture = seed_texture
   old_seed_shadow = seed_shadow
   
   show_helpers = True

   mouse_x = 0
   mouse_y = 0
   
   while run:
      w, h = scr_size
      
      minxpos = int(xpos - (w / 2))
      minypos = int(ypos - (h / 2))
      mapx = math.floor(minxpos / rmapsize)
      mapy = math.floor(minypos / rmapsize)
      mapw = math.ceil((minxpos + w) / rmapsize) - mapx
      maph = math.ceil((minypos + h) / rmapsize) - mapy

      # CURSOR POSITION
      hrsize = render_size // 2
      htsize = TILE_SIZE // 2

      offx = minxpos - minxpos // hrsize * hrsize
      offy = minypos - minypos // hrsize * hrsize
      
      tx = (mouse_x + offx) // hrsize * hrsize - offx
      ty = (mouse_y + offy) // hrsize * hrsize - offy
      
      for event in pygame.event.get():
         if event.type == pygame.QUIT: run = False
         elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 2:
               show_helpers = not show_helpers
               continue

            if event.button == 3:
               if not pathing:
                  pathing = pygame.time.get_ticks()
                  paths.append(Path(color = (255, 0, 0), points = [((ambishift(minxpos + mouse_x, -zoom) // htsize + 0.5) * htsize, (ambishift(minypos + mouse_y, -zoom) // htsize + 0.5) * htsize)]))
                  continue
               now = pygame.time.get_ticks()
               if now - pathing < 200:
                  if len(paths[-1].points) < 2: del paths[-1]
                  pathing = 0
                  continue
               
               point = ((ambishift(minxpos + mouse_x, -zoom) // htsize + 0.5) * htsize, (ambishift(minypos + mouse_y, -zoom) // htsize + 0.5) * htsize)
               if paths[-1].points[-1][0] != point[0] or paths[-1].points[-1][1] != point[1]:
                  paths[-1].points.append(point)
               pathing = now
               continue
            
            if event.button != 1: continue
            if seed_texture.get_rect().move(2, 2).collidepoint(event.pos):
               if writing_seed: continue
               
               now = pygame.time.get_ticks()
               if now - last_click < 200: start_edit_seed()
               last_click = now
               continue
            
            drag = True
            if writing_seed:
               end_edit_seed()
         elif event.type == pygame.MOUSEBUTTONUP:
            drag = False
         elif event.type == pygame.MOUSEMOTION:
            if drag:
               dx, dy = event.rel
               xpos -= dx
               ypos -= dy
            mouse_x, mouse_y = event.pos
            
         elif event.type == pygame.MOUSEWHEEL:
            old_zoom = zoom
            zoom = min(max(-5, zoom + (event.y > 0) * 2 - 1), 2)
            if zoom == old_zoom: continue
            
            render_size = ambishift(TILE_SIZE, zoom)
            xpos = ambishift(xpos, zoom - old_zoom)
            ypos = ambishift(ypos, zoom - old_zoom)
               
            rmapsize = MAP_SIZE * render_size
            
            map_cx = math.ceil(scr_size[0] / rmapsize)
            map_cy = math.ceil(scr_size[1] / rmapsize)
         
         elif event.type == pygame.VIDEORESIZE:
            scr_size = event.size
            w, h = scr_size
            map_cx = math.ceil(scr_size[0] / rmapsize)
            map_cy = math.ceil(scr_size[1] / rmapsize)
         
         elif event.type == pygame.KEYDOWN:
            if not writing_seed: continue
            
            if event.key == 27:
               end_edit_seed(True) # ESC
            elif event.key == 13: # ENTER
               end_edit_seed()
            elif event.key == 8: # RETURN
               nibble = 0
               for i, t in enumerate(new_seed):
                  t |= nibble
                  nibble = (t & 0xF) << 8
                  new_seed[i] = t >> 4
               update_seed_textures(new_seed, True)
               
         elif event.type == pygame.TEXTINPUT:
            if not writing_seed:
               print(len(map_textures))
               continue
            try: nibble = int(event.text, 16)
            except Exception: continue
            l = len(new_seed) - 1
            for i, t in enumerate(reversed(new_seed)):
               t = (t << 4) | nibble
               nibble = t >> 8
               new_seed[l - i] = t & 0xFF
            update_seed_textures(new_seed, True)
      
      for j in range(maph):
         for i in range(mapw):
            cx = (mapx + i) & 0xFFFF
            cy = (mapy + j) & 0xFFFF
            
            rcx = (mapx + i) * rmapsize - minxpos
            rcy = (mapy + j) * rmapsize - minypos
            
            map_key = f'{cx:02X}_{cy:02X}'
            map_texture = map_textures.get(map_key)
            
            if not map_texture:
               map_texture = pygame.Surface((MAP_SIZE * TILE_SIZE, MAP_SIZE * TILE_SIZE))
               biome, _ = get_biome_and_connections(cx, cy)
               curr_map = maps.get((cx, cy))
               
               if not curr_map:
                  curr_map = generate_chunk(cx, cy)
                  maps[(cx, cy)] = curr_map
               
               for n, t in enumerate(curr_map):
                  texture = textures.get(t, TEXTURE_UNKNOWN)
                  texture.set_palette(PALETTES[biome])
                  map_texture.blit(texture, ((n & 7) * TILE_SIZE, (n >> 3) * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                  
               map_textures[map_key] = map_texture

            if zoom != 0:
               map_texture = pygame.transform.scale(map_texture, (render_size * MAP_SIZE, render_size * MAP_SIZE))
            
            screen.blit(map_texture, (rcx, rcy, render_size * MAP_SIZE, render_size * MAP_SIZE))
            
            if not show_helpers: continue
            text1 = font.render(f'{cx:04X} {cy:04X}', False, (255, 255, 255))
            text2 = font.render(f'{cx:04X} {cy:04X}', False, (0, 0, 0))
            text_with_shadow(rcx + 1, rcy + 1, 1, text1, text2)
            pygame.draw.rect(screen, (127, 127, 127), (max(rcx, 0), max(rcy, 0), rmapsize + 1, rmapsize + 1), 1)

      if mapx <= 1 < mapx + mapw and mapy <= 2 < mapy + maph:
         size = max(0, zoom)
         key = f'{size}_PLAYER'
         size = (TILE_SIZE // 2) << size
         
         texture = textures.get(key)
         if not texture:
            texture = pygame.transform.scale(textures.get(f'0_PLAYER', TEXTURE_UNKNOWN), (size, size))
            textures[key] = texture

         offsety = ambishift(4, zoom)
         screen.blit(texture, (rmapsize + (spawn & 7) * render_size - minxpos, 2 * rmapsize + (spawn >> 3) * render_size - minypos - offsety, size, size))

      mult = (1 / (1 << -zoom)) if zoom < 0 else 1 << zoom
      
      if pathing:
         paths[-1].points.append(((ambishift(minxpos + mouse_x, -zoom) // htsize + 0.5) * htsize, (ambishift(minypos + mouse_y, -zoom) // htsize + 0.5) * htsize))
      
      for path in paths:
         
         maxxpos = minxpos + w
         maxypos = minypos + h
         
         for i in range(len(path.points) - 1):
            p = path.points[i]
            q = path.points[i + 1]
            minx = min(p[0], q[0]) * mult
            maxx = max(p[0], q[0]) * mult
            miny = min(p[1], q[1]) * mult
            maxy = max(p[1], q[1]) * mult
            
            if minx >= maxxpos or maxx <= minxpos or miny >= maxypos or maxy <= minypos: continue
            rp = (p[0] * mult - minxpos, p[1] * mult - minypos)
            rq = (q[0] * mult - minxpos, q[1] * mult - minypos)
            
            pygame.draw.line(screen, path.color, rp, rq, 2)
      
      if pathing:
         del paths[-1].points[-1]


      # CURSOR RENDER
      ptr_size = max(1, ambishift(TILE_SIZE, zoom - 1))
      key = f'{ptr_size}_PTR'
      
      texture = textures.get(key)
      if not texture:
         texture = pygame.transform.scale(textures.get(f'16_PTR', TEXTURE_UNKNOWN), (ptr_size, ptr_size))
         textures[key] = texture
      
      screen.blit(texture, (tx, ty, ptr_size, ptr_size))
      
      text_with_shadow(2, 2, 2, seed_texture, seed_shadow)
      pygame.display.update()
      clock.tick(60)
