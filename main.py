import pygame
import sys
import time
import random
import math  # [NEW] Cần dùng thư viện toán học để làm sóng

# --- 1. CẤU HÌNH GAME ---
GRID_SIZE = 48
COLS = 12
ROWS = 150
SCREEN_WIDTH_PX = COLS * GRID_SIZE
SCREEN_HEIGHT_PX = 16* GRID_SIZE
FPS = 60

# --- MÀU SẮC ---
COLOR_SAND = (244, 164, 96)
COLOR_EXIT = (200, 200, 100)
COLOR_SHELL = (255, 250, 240)    
COLOR_STARFISH = (255, 105, 180) 
COLOR_LOG = (139, 69, 19)        
COLOR_TURTLE = (34, 139, 34)
COLOR_TURTLE_STUN = (100, 100, 100)
COLOR_TURTLE_SLOW = (0, 0, 255)
COLOR_CRAB = (220, 20, 60)        
COLOR_SEAGULL = (25, 25, 112)
COLOR_HOLE = (20, 20, 20)        
COLOR_POPUP_BG = (50, 50, 50)    
COLOR_TEXT = (255, 255, 255)


# [NEW] MÀU BIỂN
COLOR_SEA_DEEP = (0, 0, 139)      # Xanh biển sâu (Win)
COLOR_SEA_FOAM = (0, 191, 255)    # Xanh mép sóng (Chưa Win)
COLOR_WIN_OVERLAY = (0, 255, 0)   # Màu thông báo thắng
#Map
def load_map(file_path):
    temp_map = []
    with open(file_path, "r") as f:
        for line in f:
            # Xử lý từng dòng: bỏ khoảng trắng, tách dấu phẩy, chuyển thành số
            row = [int(x) for x in line.strip().split(",") if x.strip()]
            temp_map.append(row)
    return temp_map

# Gọi hàm để nạp bản đồ từ file
GAME_MAP = load_map("map.txt")

# Tự động cập nhật số hàng và cột để code không bị lỗi
ROWS = len(GAME_MAP)
COLS = len(GAME_MAP[0]) if ROWS > 0 else 20

# --- 3. CLASS & LOGIC ---

class Crab:
    def __init__(self, x_grid, y_grid, direction, type_move, zone_min_y, zone_max_y):
        self.x = x_grid * GRID_SIZE
        self.y = y_grid * GRID_SIZE
        self.direction = direction 
        self.speed = 2 
        self.type_move = type_move 
        self.min_y = zone_min_y * GRID_SIZE
        self.max_y = zone_max_y * GRID_SIZE
        
    def update(self):
        if self.type_move == 'horizontal':
            self.x += self.speed * self.direction
            if self.x <= 0 or self.x >= SCREEN_WIDTH_PX - GRID_SIZE:
                self.direction *= -1
        elif self.type_move == 'vertical':
            self.y += self.speed * self.direction
            if self.y <= self.min_y or self.y >= self.max_y:
                self.direction *= -1
                
    def draw(self, screen, camera_y):
        draw_y = self.y - camera_y

    # Kiểm tra nếu cua nằm trong màn hình thì mới vẽ
        if -GRID_SIZE < draw_y < SCREEN_HEIGHT_PX:
        # VẼ ẢNH CUA TẠI ĐÂY
             screen.blit(crab_img, (self.x, draw_y))

class Seagull:
    def __init__(self, x_grid, y_grid, direction, type_move='horizontal'):
        self.x = x_grid * GRID_SIZE
        self.y = y_grid * GRID_SIZE
        self.direction = direction
        self.speed = 3
        self.type_move = type_move
        self.min_y_zone3 = 0
        self.max_y_zone3 = 60 * GRID_SIZE

    def update(self):
        if self.type_move == 'horizontal':
            self.x += self.speed * self.direction
            if self.direction == 1 and self.x > SCREEN_WIDTH_PX:
                self.x = -GRID_SIZE 
            elif self.direction == -1 and self.x < -GRID_SIZE:
                self.x = SCREEN_WIDTH_PX 
        
        elif self.type_move == 'vertical':
            self.y += self.speed * self.direction
            if self.direction == 1 and self.y > self.max_y_zone3:
                self.y = -GRID_SIZE 
            elif self.direction == -1 and self.y < -GRID_SIZE:
                self.y = self.max_y_zone3

    def draw(self, screen, camera_y, player_x_px, player_y_px):
        draw_y = self.y - camera_y
        dist_x = abs(self.x - player_x_px)
        dist_y = abs(draw_y - (player_y_px - camera_y))
        dist_tiles = (dist_x + dist_y) / GRID_SIZE
        VISIBILITY_RANGE = 5.0
        
        if dist_tiles <= VISIBILITY_RANGE:
            alpha = int(255 * (1 - (dist_tiles / VISIBILITY_RANGE)))
            if alpha < 0: alpha = 0
            if alpha > 255: alpha = 255
            

           # ... (Giữ nguyên đoạn tính toán alpha ở trên nếu muốn) ...
            
            if -GRID_SIZE < draw_y < SCREEN_HEIGHT_PX:
                # Vẽ ảnh Hải Âu
                screen.blit(seagull_img, (self.x, draw_y))

# --- KHỞI TẠO GAME ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH_PX, SCREEN_HEIGHT_PX))
pygame.display.set_caption("Turtle Run - Wave Logic")
clock = pygame.time.Clock()
font_popup = pygame.font.SysFont(None, 40)
font_small = pygame.font.SysFont(None, 24)
# PLAYER SETUP
player_x = COLS // 2
player_y = ROWS - 135
last_move_time = 0
MOVE_COOLDOWN_NORMAL = 0.05
MOVE_COOLDOWN_SLOW = 0.4 
camera_y = (ROWS * GRID_SIZE) - SCREEN_HEIGHT_PX 
# --- KHU VỰC NẠP ẢNH ---
turtle_img = pygame.image.load("assets/rua.png")
crab_img = pygame.image.load("assets/cua.png")
seagull_img = pygame.image.load("assets/haiau.png") # Nhớ tên file là haiau.png nhé
# Nạp ảnh nền cát
sand_img = pygame.image.load("assets/cat.png").convert() 
# Nạp ảnh nền toàn bản đồ
background_img = pygame.image.load("assets/nen.png").convert()

# Resize cho đúng kích thước toàn bộ bản đồ game


# Xử lý trong suốt
turtle_img = turtle_img.convert_alpha()
crab_img = crab_img.convert_alpha()
seagull_img = seagull_img.convert_alpha()

# Resize về 40x40
turtle_img = pygame.transform.scale(turtle_img, (GRID_SIZE, GRID_SIZE))
crab_img = pygame.transform.scale(crab_img, (GRID_SIZE, GRID_SIZE))
seagull_img = pygame.transform.scale(seagull_img, (GRID_SIZE, GRID_SIZE))
sand_img = pygame.transform.scale(sand_img, (GRID_SIZE, GRID_SIZE))
total_map_height = ROWS * GRID_SIZE
background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH_PX, total_map_height))

# --- RESET GAME ---
def reset_game():
    global player_x, player_y, stun_end_time, slow_end_time, last_move_time, camera_y
    player_x = COLS // 2
    player_y = ROWS - 1 
    stun_end_time = 0
    slow_end_time = 0
    last_move_time = 0
    camera_y = (ROWS * GRID_SIZE) - SCREEN_HEIGHT_PX 

# --- SETUP ENEMIES ---
crabs = []
seagulls = []

# ZONE 2 CRABS
for i in range(65, 115, 5): 
    direction = 1 if i % 2 == 0 else -1
    crabs.append(Crab(random.randint(0, 15), i, direction, 'horizontal', 0, 0))
crabs.append(Crab(3, 70, 1, 'vertical', 70, 90))
crabs.append(Crab(16, 90, 1, 'vertical', 90, 110))
crabs.append(Crab(16, 140, 1, 'vertical', 140, 150))

# ZONE 3 CRABS
for i in range(5, 55, 8):
    crabs.append(Crab(random.randint(0, 15), i, 1, 'horizontal', 0, 0))
crabs.append(Crab(8, 10, 1, 'vertical', 10, 30))

# ZONE 3 SEAGULLS
seagulls.append(Seagull(0, 10, 1, 'horizontal')) 
seagulls.append(Seagull(15, 25, -1, 'horizontal'))
seagulls.append(Seagull(5, 40, 1, 'horizontal'))
seagulls.append(Seagull(5, 0, 1, 'vertical')) 
seagulls.append(Seagull(14, 50, -1, 'vertical'))
seagulls.append(Seagull(18, 10, 1, 'vertical'))
seagulls.append(Seagull(5, 147, 1, 'horizontal'))



# LOGIC VARIABLES
OBSTACLES = [1, 2, 3] 
hole_timer = 0         
is_in_hole = False     
showed_popup_z2 = False 
showed_popup_z3 = False
game_state = "PLAYING"
stun_end_time = 0 
slow_end_time = 0 
current_popup_msg = "" 

# --- GAME LOOP ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_state == "PAUSED" or game_state == "WIN":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if game_state == "WIN":
                        reset_game()
                    game_state = "PLAYING"

    if game_state == "PLAYING":
        current_time = time.time()
        
      
        # 1. Popup hướng dẫn
        if player_y <= 119 and player_y > 59 and not showed_popup_z2:
            game_state = "PAUSED"
            showed_popup_z2 = True
            current_popup_msg = "ZONE 2: CUA DI TUAN!"
            
        if player_y <= 59 and not showed_popup_z3:
            game_state = "PAUSED"
            showed_popup_z3 = True
            current_popup_msg = "ZONE 3: TEST HAI AU DOC & NGANG!"

        # 2. Update Kẻ thù
        for crab in crabs: crab.update()
        for bird in seagulls: bird.update()
            
        # 3. Player Status
        is_stunned = current_time < stun_end_time
        is_slowed = current_time < slow_end_time
        current_cooldown = MOVE_COOLDOWN_SLOW if is_slowed else MOVE_COOLDOWN_NORMAL

        # 4. HANG (Anti-Camping)
        current_tile = GAME_MAP[player_y][player_x]
        if current_tile == 4: 
            if not is_in_hole:
                is_in_hole = True
                hole_start_time = time.time()
            hole_timer = time.time() - hole_start_time
            if hole_timer > 3.0: 
                if player_y + 1 < ROWS: player_y += 1 
                else: player_y -= 1
                is_in_hole = False
                hole_timer = 0
                stun_end_time = current_time + 1.0 
        else:
            is_in_hole = False
            hole_timer = 0

        # 5. Move
        keys = pygame.key.get_pressed()
        if not is_stunned: 
            if current_time - last_move_time > current_cooldown:
                dx, dy = 0, 0
                if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -1
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = 1
                if keys[pygame.K_UP] or keys[pygame.K_w]: dy = -1
                if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy = 1
                
                if dx != 0 or dy != 0:
                    new_x = player_x + dx
                    new_y = player_y + dy
                    if 0 <= new_x < COLS and 0 <= new_y < ROWS:
                        if GAME_MAP[new_y][new_x] not in OBSTACLES:
                            player_x = new_x
                            player_y = new_y
                            last_move_time = current_time

        # 6. Collision Check (Kẻ thù)
        player_rect = pygame.Rect(player_x * GRID_SIZE, player_y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        
        if not is_in_hole:
            for crab in crabs:
                crab_rect = pygame.Rect(crab.x, crab.y, GRID_SIZE, GRID_SIZE)
                if player_rect.colliderect(crab_rect):
                    if not is_stunned:
                        if player_y + 1 < ROWS: player_y += 1
                        stun_end_time = current_time + 1.0 
                        slow_end_time = current_time + 4.0 
            
            for bird in seagulls:
                bird_rect = pygame.Rect(bird.x, bird.y, GRID_SIZE, GRID_SIZE)
                if player_rect.colliderect(bird_rect):
                    reset_game() 
                    game_state = "PAUSED"
                    current_popup_msg = "GAME OVER! VE BAI CAT..."

        # --- [NEW] CHECK WIN CONDITION VỚI SÓNG ---
        # Chỉ check khi người chơi lên tới vùng 4 hàng đầu (y < 4)
        # --- CHECK WIN THEO MAP (SỐ 9) ---
        # Kiểm tra ô rùa đang đứng (Check ngay lập tức, không quan tâm Y bằng bao nhiêu)
        current_tile = GAME_MAP[player_y][player_x]

        # Nếu rùa dẫm vào ô số 9 -> Thắng ngay lập tức
        if current_tile == 9:
            game_state = "WIN"
            current_popup_msg = "YOU WIN! RUA VE BIEN KHOI!"

    # --- RENDER ---
    
    # Camera Shake
    shake_x, shake_y = 0, 0
    if is_in_hole and hole_timer > 2.0:
        shake_x = random.randint(-5, 5)
        shake_y = random.randint(-5, 5)

    target_cam_y = (player_y * GRID_SIZE) - (SCREEN_HEIGHT_PX // 2)
    max_scroll = (ROWS * GRID_SIZE) - SCREEN_HEIGHT_PX
    if target_cam_y < 0: target_cam_y = 0
    if target_cam_y > max_scroll: target_cam_y = max_scroll
    camera_y = target_cam_y

    # --- RENDER ---
# 1. Vẽ ảnh nền to toàn bản đồ (PHẢI VẼ TRƯỚC VÒNG LẶP)
# Toạ độ (0, -camera_y) giúp toàn bộ bãi cát trôi theo bước chân của rùa
    screen.blit(background_img, (0, -camera_y)) 

# 2. Vẽ các vật thể (Vỏ sò, Cua, Gỗ...) đè lên nền cát
    for r in range(ROWS):
    # Skip 4 hàng đầu nếu đó là vùng sóng biển em tự vẽ bằng code
       
    
       for c in range(COLS):
           val = GAME_MAP[r][c]
        
        # QUAN TRỌNG: Chỉ vẽ nếu ô đó là vật thể (val != 0)
        # Chúng ta không vẽ sand_img ở đây nữa vì đã có background_img ở trên
           if val != 0 and val != 9:
               draw_x = c * GRID_SIZE + shake_x
               draw_y = (r * GRID_SIZE) - camera_y + shake_y
            
            # Chỉ tính toán và vẽ nếu vật thể nằm trong màn hình để đỡ lag
               if -GRID_SIZE <= draw_y <= SCREEN_HEIGHT_PX:
                   rect = pygame.Rect(draw_x, draw_y, GRID_SIZE, GRID_SIZE)
                
                # Vẽ các vật thể dựa theo giá trị trong GAME_MAP
                   if val == 1:
                       pygame.draw.rect(screen, COLOR_SHELL, rect) # Vỏ sò
                   elif val == 2:
                       pygame.draw.rect(screen, COLOR_STARFISH, rect) # Sao biển
                   elif val == 3:
                       pygame.draw.rect(screen, COLOR_LOG, rect) # Khúc gỗ
                   elif val == 4:
                       pygame.draw.rect(screen, COLOR_HOLE, rect) # Hang cua
    # BỎ DÒNG VẼ VIỀN XÁM (rect, 1) ĐỂ CÁT TRÔNG LIỀN MẠCH
            
    # 2. [NEW] Vẽ Sóng Biển (Dynamic)
    # Chúng ta vẽ đè lên 4 hàng đầu tiên (Row 0, 1, 2, 3)
    # Lấy lại giá trị deep_sea_limit đã tính ở phần Logic
    
    # 3. Vẽ Entities
    for crab in crabs: crab.draw(screen, camera_y)
    
    p_real_x = player_x * GRID_SIZE
    p_real_y = player_y * GRID_SIZE
    for bird in seagulls: 
        bird.draw(screen, camera_y, p_real_x, p_real_y)

    # 4. Vẽ Rùa
    current_turtle_color = COLOR_TURTLE 
    if current_time < stun_end_time: current_turtle_color = COLOR_TURTLE_STUN 
    elif current_time < slow_end_time: current_turtle_color = COLOR_TURTLE_SLOW 
    draw_px = player_x * GRID_SIZE + shake_x
    draw_py = (player_y * GRID_SIZE) - camera_y + shake_y
    
    # Nếu rùa chui vào vùng biển sâu thì rùa mờ đi một chút (chìm xuống nước)
    if player_y < 4: # Ở vùng biển
         pass # Có thể thêm hiệu ứng ở đây nếu thích
         
    screen.blit(turtle_img, (draw_px, draw_py))

    # 5. Popup & UI
# --- 5. Popup & UI (Căn chỉnh tự động cho Game Thùng) ---
    if game_state == "PAUSED" or game_state == "WIN":
    # 1. Tính toán kích thước bảng dựa trên màn hình hiện tại
       popup_w = SCREEN_WIDTH_PX * 0.8  # Rộng bằng 80% màn hình
       popup_h = SCREEN_HEIGHT_PX * 0.3 # Cao bằng 30% màn hình
    
    # 2. Tính toạ độ để bảng luôn nằm chính giữa
       popup_x = (SCREEN_WIDTH_PX - popup_w) // 2
       popup_y = (SCREEN_HEIGHT_PX - popup_h) // 2
    
       popup_rect = pygame.Rect(popup_x, popup_y, popup_w, popup_h)
    
    # Vẽ nền bảng
       bg_color = COLOR_WIN_OVERLAY if game_state == "WIN" else COLOR_POPUP_BG
       pygame.draw.rect(screen, bg_color, popup_rect)
       pygame.draw.rect(screen, (255, 255, 255), popup_rect, 3) # Viền trắng dầy hơn (3px)

    # 3. Căn chữ nằm giữa bảng (Dùng logic get_rect)
    # Dòng thông báo chính
       msg1 = font_popup.render(current_popup_msg, True, COLOR_TEXT)
       msg1_rect = msg1.get_rect(center=(popup_rect.centerx, popup_rect.centery - 20))
       screen.blit(msg1, msg1_rect)
    
    # Dòng hướng dẫn phụ
       msg2 = font_small.render("Press SPACE to continue...", True, (255, 255, 0))
       msg2_rect = msg2.get_rect(center=(popup_rect.centerx, popup_rect.centery + 30))
       screen.blit(msg2, msg2_rect)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
