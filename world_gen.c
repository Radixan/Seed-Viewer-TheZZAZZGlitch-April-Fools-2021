#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

uint8_t world_seed[] = {0x00, 0x00, 0x00, 0x00};
uint8_t current_seed[] = {0x00, 0x00, 0x00, 0x00};
uint8_t map_size = 8;
uint8_t mem_map[64] = {0x0f};
uint8_t mem_cpy[64] = {0x0f};

uint8_t DD0C[] = {0x05,0x0B,0x06,0x00,0x0E,0x05,0x0B,0x03,0x09,0x0E,0x00,0x00,0x00,0x0C,0x00,0x00,0x00,0x0C,0x05,0x06,0x06,0x0D,0x0A,0x09,0x09,0x0B,0x06,0x00,0x00,0x05,0x0A,0x00,0x05,0x0B,0x06,0x00,0x0B,0x06,0x09,0x07,0x00,0x09,0x07,0x0A,0x00,0x05,0x0A,0x00,0x00,0x09,0x06,0x00,0x03,0x06,0x0C,0x05,0x00,0x09,0x0F,0x0A,0x00,0x05,0x0A,0x00,0x05,0x0A,0x00,0x00,0x0F,0x06,0x05,0x03,0x09,0x0F,0x0A,0x00,0x00,0x0C,0x00,0x00,0x05,0x0B,0x03,0x06,0x0E,0x00,0x00,0x0D,0x09,0x06,0x00,0x0C,0x00,0x0D,0x03,0x0A,0x00,0x09,0x06,0x00,0x06,0x05,0x0A,0x05,0x09,0x0F,0x06,0x0C,0x00,0x0C,0x09,0x0A,0x00,0x0C,0x00,0x00,0x03,0x0F,0x07,0x03,0x00,0x0D,0x0A,0x00,0x00,0x0C,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00};

uint8_t ff95 = 0;
uint8_t ff96 = 0;
uint8_t ff97 = 0x10;

uint8_t ff98 = 0;
uint8_t ff99 = 0;
uint8_t ff9A = 0;
uint8_t ff9B = 0;

void nextRandom() {
  uint8_t a = current_seed[0];
  a += 1;
  current_seed[0] = a & 0xFF;
  uint8_t b = a;
  a = current_seed[3];
  a ^= b;
  b = a;
  a = current_seed[1];
  a ^= b;
  current_seed[1] = a & 0xFF;
  b = a;
  a = current_seed[2];
  a += b;
  a &= 0xFF;
  current_seed[2] = a;
  a >>= 1;
  a ^= b;
  b = a;
  a = current_seed[3];
  a += b;
  current_seed[3] = a & 0xFF;
}

void generateFromSeed(uint16_t x, uint16_t y) {
  current_seed[0] = world_seed[0] ^ (x >> 8);
  current_seed[1] = world_seed[1] ^ (x & 0xff);
  current_seed[2] = world_seed[2] ^ (y >> 8);
  current_seed[3] = world_seed[3] ^ (y & 0xff);
  for (int i = 0; i < 16; ++i) nextRandom();
}

void setZoneTypeAndConditions(uint16_t x, uint16_t y) {
  generateFromSeed(x & 0xfffc, y & 0xfffc);
  nextRandom();
  
  uint8_t rand1 = DD0C[(x & 3) + (y & 3) * 4 + ((current_seed[3] & 0x07) << 4)];
  
  nextRandom();
  uint8_t rand2 = current_seed[3];

  if (x | y & 0xfffc) ff95 = (rand2 & 0x30 | rand1);
  else ff95 = ((x & 3) + (y & 3) * 4) & 0x0F;
}

void expand() {
  memcpy(mem_cpy, mem_map, 64);
  for (int i = 8; i < 56; ++i) {
    if (ff97 != mem_cpy[i] || !(7 > (i & 0x7) && (i & 0x7) > 0)) continue;
    nextRandom();
    uint8_t direction = current_seed[3];
    if (direction & 1) mem_map[i - 1] = ff97;
    if (direction & 2) mem_map[i + 1] = ff97;
    if (direction & 4) mem_map[i - 8] = ff97;
    if (direction & 8) mem_map[i + 8] = ff97;
  }
}
		     
void traceline(uint8_t x1, uint8_t y1, uint8_t x2, uint8_t y2) {
  uint8_t xi = 1 - ((x2 < x1) << 1);
  uint8_t yi = 1 - ((y2 < y1) << 1);
  while (1) {
    mem_map[x1 + y1 * map_size] = ff97;
    if (x1 != x2) x1 += xi;
    mem_map[x1 + y1 * map_size] = ff97;
    if (y1 != y2) y1 += yi;
    mem_map[x1 + y1 * map_size] = ff97;
    
    if (x1 == x2 && y1 == y2) break;
  }
}

void traceline_through_random(uint8_t x1, uint8_t y1, uint8_t x2, uint8_t y2){
  uint8_t x, y;
  do {
    nextRandom();
    x = current_seed[3] & 0x07;
  } while ((x & 0x07) == 0x00 || x == 0x07);

  do {
    nextRandom();
    y = current_seed[3] & 0x07;
  } while ((y & 0x07) == 0x00 || y == 0x07);
   
  traceline(x1, y1, x, y);
  traceline(x, y, x2, y2);
}
					    
char* to_print = "---------- \"---#"		\
  "----------------"				\
  "----------------"				\
  "----------------"				\
  "----------------"				\
  "----------------"				\
  "------------CDEF"				\
  "----*-----+-----"				\
  "----------------"				\
  "----------------"				\
  "----------------"				\
  "----------------"				\
  "----------------"				\
  "----------------"				\
  "----------------"						\
  "---------------X";

void print_map() {
  for (int i = 0; i < 8; ++i) {
    for (int j = 0; j < 8; ++j) {
      printf("%c", to_print[mem_map[i*8+j]]);
    }
    printf("\n");
  }
  //printf("===================\n");
}

void replace_with_chance(uint8_t prob, uint8_t src, uint8_t dst){
  for (int i = 0; i < 0x40; ++i) {
    if (mem_map[i] == src) {
      nextRandom();
      if (current_seed[3] < prob) mem_map[i] = dst;
    }
  }
}

void replace_with_chance_and_neighborship(uint8_t prob, uint8_t src, uint8_t dest) {
  for (int it = 8; it < 56; ++it) {
    if (mem_map[it] != src || !(7 > (it & 0x07) && (it & 0x07) > 0)) continue;
    nextRandom();
    if (current_seed[3] < prob) continue;
    if ((ff98 && mem_map[it - 8] != ff98) ||  
	(ff99 && mem_map[it + 8] != ff99) || 
	(ff9A && mem_map[it - 1] != ff9A) || 
	(ff9B && mem_map[it + 1] != ff9B))
      continue;
    mem_map[it] = dest;
  }
}

void grasslands_generator() {
  replace_with_chance(0x30, 0x0A, 0x0B);
  ff97 = 0x0B;
  expand();
  
  ff98 = 0x0F;
  ff99 = 0x0A;
  ff9A = 0x00;
  ff9B = 0x00;
  
  replace_with_chance_and_neighborship(0x20, 0x0F, 0x6C);
  
  ff98 = 0x0A;
  ff99 = 0x0F;
  
  replace_with_chance_and_neighborship(0x20, 0x0F, 0x6F);
  
  ff98 = 0x00;
  ff99 = 0x00;
  ff9A = 0x0A;
  ff9B = 0x0F;
  
  replace_with_chance_and_neighborship(0x20, 0x0F, 0x6E);
  
  ff9A = 0x0F;
  ff9B = 0x0A;
  
  replace_with_chance_and_neighborship(0x20, 0x0F, 0x6D);
  
  replace_with_chance(0x30, 0x0A, 0x74);
  replace_with_chance(0x30, 0x0A, 0x7A);
}

void generateBlockMap(uint16_t x, uint16_t y) {
    setZoneTypeAndConditions(x,y);
    memset(mem_map, 0x0f, 64);
     
    ff97 = 0x0A;
        
    if (ff95 & 1) ff96 = 0x74;
    if (ff95 & 2) ff96 = 0x04;
    if (ff95 & 4) ff96 = 0x47;
    if (ff95 & 8) ff96 = 0x40;
    
    generateFromSeed(x, y);
    uint8_t ff96_h = ff96 >> 4;
    uint8_t ff96_l = ff96 & 0xF;
    
    if (ff95 & 1) traceline_through_random(ff96_h, ff96_l, 0x7, 0x4);
    if (ff95 & 2) traceline_through_random(ff96_h, ff96_l, 0x0, 0x4);
    if (ff95 & 4) traceline_through_random(ff96_h, ff96_l, 0x4, 0x7);
    if (ff95 & 8) traceline_through_random(ff96_h, ff96_l, 0x4, 0x0);
    
    ff97 = 0x0A;
    expand();
    
    if (ff95 & 8) {
      mem_map[3               ] = ff97;
      mem_map[4               ] = ff97;
    }
    if (ff95 & 4) {
      mem_map[3 + 7 * map_size] = ff97;
      mem_map[4 + 7 * map_size] = ff97;
    }
    if (ff95 & 2) {
      mem_map[    3 * map_size] = ff97;
      mem_map[    4 * map_size] = ff97;
    }
    if (ff95 & 1) {
      mem_map[7 + 3 * map_size] = ff97;
      mem_map[7 + 4 * map_size] = ff97;
    }
        
    grasslands_generator();
}

uint8_t big[64*9] = {0};

void copyMap(uint8_t x, uint8_t y) {
  for (int i = 0; i < 8; ++i) {
    for (int j = 0; j < 8; ++j){
      big[y*8*8*3 + x*8 + i*8*3 + j] = mem_map[i*8+j];
    }
  }
}

void print_big() {
  for (int i = 0; i < 8*3; ++i) {
    for (int j = 0; j < 8*3; ++j) {
      printf("%c", to_print[big[i*8*3+j]]);
    }
    printf("\n");
  }
  //printf("===================\n");
}

uint8_t getBIGBlock(uint8_t x, uint8_t y) {
  return big[x+y*24];
}

int main(int argc, char* argv[]) {
   uint32_t it = 0x65000001; //0x01;
   /*   generateBlockMap(1, 2);
   print_map();

   return 0;*/
   
   uint8_t row1[] = {0x0F,0x0B,0x0F,0x0A,0x0A};
   uint8_t row2[] = {0x0F,0x0F,0x0A,0x0A,0x0B};
   uint8_t row3[] = {0x0F,0x0B,0x0A,0x0A,0x0A};
   uint8_t row4[] = {0x0B,0x0B,0x0A,0x0A,0x74};
   
   while (1) {
     world_seed[0] = (it >> 24) & 0xff;
     world_seed[1] = (it >> 16) & 0xff;
     world_seed[2] = (it >> 8) & 0xff;
     world_seed[3] = (it) & 0xff;
     generateBlockMap(0, 1);
     copyMap(0, 0);
     generateBlockMap(1, 1);
     copyMap(1, 0);
     generateBlockMap(2, 1);
     copyMap(2, 0);
     generateBlockMap(0, 2);
     copyMap(0, 1);
     generateBlockMap(1, 2);
     copyMap(1, 1);

     uint8_t slot = 0;
     for (slot = 0; slot < 64 && mem_map[slot] != 0x0A; slot++);
     //printf("Spawn at: %d\n", slot);

     uint8_t px = slot % 8 + 8;
     uint8_t py = slot / 8 + 8;

     big[px + py * 24] = 0xFF;

     generateBlockMap(2, 2);
     copyMap(2, 1);
     generateBlockMap(0, 3);
     copyMap(0, 2);
     generateBlockMap(1, 3);
     copyMap(1, 2);
     generateBlockMap(2, 3);
     copyMap(2, 2);
     /*
     printf("\033[2J\033[H");
     printf("%02x %02x %02x %02x\n", (it >> 24) & 0xff, (it >> 16) & 0xff, (it >> 8) & 0xff, (it) & 0xff);
     print_map();*/
    printf("\r%02x %02x %02x %02x", (it >> 24) & 0xff, (it >> 16) & 0xff, (it >> 8) & 0xff, (it) & 0xff);

    if (getBIGBlock(px + 1, py - 2) != 0x74) goto next;
    if (getBIGBlock(px + 2, py + 2) != 0x74) goto next;

    if (getBIGBlock(px, py -1) != 0x0F) goto next;
    if (getBIGBlock(px - 1, py) != 0x0F) goto next;
    
    if (getBIGBlock(px - 1, py -1) != 0x0B) goto next;
    if (getBIGBlock(px - 2, py -1) != 0x0F) goto next;
    if (getBIGBlock(px - 2, py) != 0x0F) goto next;
    if (getBIGBlock(px - 2, py + 1) != 0x0F) goto next;
    
    if (getBIGBlock(px - 1, py + 1) != 0x0B) goto next;
    if (getBIGBlock(px - 1, py + 2) != 0x0B) goto next;
    if (getBIGBlock(px - 2, py + 2) != 0x0B) goto next;
    
    if (getBIGBlock(px + 2, py) != 0x0B) goto next;
    if (getBIGBlock(px, py - 2) != 0x0B) goto next;
    if (getBIGBlock(px - 1, py - 2) != 0x0B) goto next;
    if (getBIGBlock(px - 2, py - 2) != 0x0B) goto next;
     
     
     if (getBIGBlock(px + 2, py - 2) != 0x0A) goto next;
     if (getBIGBlock(px + 2, py - 1) != 0x0A) goto next;
     if (getBIGBlock(px + 1, py - 1) != 0x0A) goto next;
     if (getBIGBlock(px + 1, py) != 0x0A) goto next;
     if (getBIGBlock(px, py + 1) != 0x0A) goto next;
     if (getBIGBlock(px + 1, py + 1) != 0x0A) goto next;
     if (getBIGBlock(px + 2, py + 1) != 0x0A) goto next;
         
     //if mem_map[0:5] == row_1 and mem_map[8:13] == row_2 and mem_map[16:21] == row_3: break

     //if (mem_map[0] != 0x0F) goto next;
     //if (mem_map[1] != 0x0F) goto next;
     
     /*if (mem_map[0] != 0x0F) goto next;
     if (mem_map[1] != 0x0B) goto next;
     if (mem_map[2] != 0x0F) goto next;
     if (mem_map[3] != 0x0A) goto next;
     if (mem_map[4] != 0x0A) goto next;

     if (mem_map[8] != 0x0F) goto next;
     if (mem_map[9] != 0x0F) goto next;*/
     
     
     //for (int i = 0; i <= 5; ++i) if (mem_map[0+i] != row1[i]) goto next;
     //for (int i = 0; i <= 5; ++i) if (mem_map[8+i] != row2[i]) goto next;
     //for (int i = 0; i <= 5; ++i) if (mem_map[16+i] != row3[i]) goto next;

     //break;
     printf("\n");
     print_big();
     printf("\n");
   next:
     it += 0x10;
   }
   printf("\n");
   print_big();
}
