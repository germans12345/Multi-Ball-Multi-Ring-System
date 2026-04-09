# =====================================
# 项目5 最终调参版（录屏展示优化版）
# 1. 多圆环动态系统
# 2. 动态缺口（旋转）
# 3. 多球系统
# 4. 每个球独立 layer
# 5. 支持层间穿越
# 6. 同层球球碰撞
# 7. 最外层缺口逃出
# 8. 所有球逃完自动进入下一轮
# 9. 节奏系统升级（群体节奏感）
# 10. 成片优化（特效分层 / 视觉降噪 / 高潮突出）
# 11. 最终调参（更适合录屏展示）
# =====================================

# ========= 1. 导入库 =========
import pygame
import sys
import math
import random

# ========= 2. 初始化 pygame =========
pygame.init()
pygame.font.init()

# ========= 3. 创建窗口 =========
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("项目5 最终调参版（录屏展示优化版）")

# ========= 4. 时钟 =========
clock = pygame.time.Clock()

# ========= 5. 创建拖尾图层 =========
fade_surface = pygame.Surface((WIDTH, HEIGHT))
fade_surface.set_alpha(20)
fade_surface.fill((0, 0, 0))

# ========= 6. 圆心位置 =========
center_x = WIDTH // 2
center_y = HEIGHT // 2

# =====================================
# ========= 7. 节奏系统 =========
# =====================================
rhythm = 0

def update_rhythm():
    """
    更新节奏变量

    最终调参版里，把节奏略收一点：
    - 保留群体感
    - 但避免节奏过满导致画面太忙
    """
    global rhythm
    rhythm += 0.022

def get_global_pulse():
    """
    获取全局脉冲值
    返回范围大致在 0 ~ 1
    """
    return 0.5 + 0.5 * math.sin(rhythm * 2.0)

# =====================================
# ========= 8. 圆环系统 =========
# =====================================
GAP_SIZE = 50
RING_SPACING = 95
BASE_RADIUS = 120

ring_base_speeds = [0.28, -0.44, 0.66]

rings = []
for i in range(3):
    rings.append({
        "radius": BASE_RADIUS + i * RING_SPACING,
        "gap_start": 0,
        "gap_end": 0,
        "base_speed": ring_base_speeds[i]
    })

def randomize_gap(ring):
    """
    随机生成单个圆环的缺口
    """
    gap_center = random.randint(0, 359)
    ring["gap_start"] = (gap_center - GAP_SIZE // 2) % 360
    ring["gap_end"] = (gap_center + GAP_SIZE // 2) % 360

def randomize_all_gaps():
    """
    为所有圆环随机生成缺口
    """
    for ring in rings:
        randomize_gap(ring)

def is_angle_in_gap(angle, ring):
    """
    判断某个角度是否在指定圆环缺口中
    支持跨 0° 的情况
    """
    if ring["gap_start"] <= ring["gap_end"]:
        return ring["gap_start"] <= angle <= ring["gap_end"]
    else:
        return angle >= ring["gap_start"] or angle <= ring["gap_end"]

# =====================================
# ========= 9. 多球系统 =========
# =====================================
BALL_COUNT = 5
BALL_RADIUS = 10
MIN_BALL_SPEED = 2.7
MAX_BALL_SPEED = 4.4

BALL_COLORS = [
    (255, 200, 120),
    (255, 160, 120),
    (255, 220, 150),
    (255, 180, 90),
    (255, 210, 100),
]

balls = []

def create_one_ball(index):
    """
    创建一个小球
    """
    angle = random.uniform(0, 2 * math.pi)
    speed = random.uniform(3.0, 3.6)

    return {
        "x": center_x + random.uniform(-10, 10),
        "y": center_y + random.uniform(-10, 10),
        "vx": math.cos(angle) * speed,
        "vy": math.sin(angle) * speed,
        "radius": BALL_RADIUS,
        "color": BALL_COLORS[index % len(BALL_COLORS)],
        "layer": 0,
        "escaped": False,
        "layer_timer": 0,
        "last_layer": 0,
        "pulse_offset": random.uniform(0, math.pi * 2),
    }

def create_balls():
    """
    批量创建多个小球
    """
    balls.clear()
    for i in range(BALL_COUNT):
        balls.append(create_one_ball(i))

# =====================================
# ========= 10. 轮次系统 =========
# =====================================
current_round = 1
round_clear_timer = 0
ROUND_CLEAR_DELAY = 78

font = pygame.font.Font(None, 24)
small_font = pygame.font.Font(None, 18)

def all_balls_escaped():
    """
    判断是否所有小球都已经逃出
    """
    for ball in balls:
        if not ball["escaped"]:
            return False
    return True

def reset_round():
    """
    重置新一轮
    """
    randomize_all_gaps()
    create_balls()
    particles.clear()
    shockwaves.clear()

# =====================================
# ========= 11. 数学辅助函数 =========
# =====================================
def get_dxdy(ball):
    """
    获取某个小球相对圆心的位移
    """
    return ball["x"] - center_x, ball["y"] - center_y

def get_dist(ball):
    """
    获取某个小球到圆心的距离
    """
    dx, dy = get_dxdy(ball)
    return math.sqrt(dx * dx + dy * dy)

def get_angle(ball):
    """
    获取某个小球相对圆心的角度（0~360）
    """
    dx, dy = get_dxdy(ball)
    angle = math.degrees(math.atan2(dy, dx))
    if angle < 0:
        angle += 360
    return angle

def get_ball_speed(ball):
    """
    获取当前小球速度大小
    """
    return math.sqrt(ball["vx"] ** 2 + ball["vy"] ** 2)

def clamp_ball_speed(ball):
    """
    限制某个小球的速度范围
    """
    speed = get_ball_speed(ball)

    if speed == 0:
        angle = random.uniform(0, 2 * math.pi)
        ball["vx"] = math.cos(angle) * MIN_BALL_SPEED
        ball["vy"] = math.sin(angle) * MIN_BALL_SPEED
        return

    if speed < MIN_BALL_SPEED:
        scale = MIN_BALL_SPEED / speed
        ball["vx"] *= scale
        ball["vy"] *= scale

    elif speed > MAX_BALL_SPEED:
        scale = MAX_BALL_SPEED / speed
        ball["vx"] *= scale
        ball["vy"] *= scale

# =====================================
# ========= 12. 防锁死系统 =========
# =====================================
def add_angular_noise(ball, amount=0.05):
    """
    给碰撞后的速度方向增加微小扰动
    """
    angle = math.atan2(ball["vy"], ball["vx"])
    speed = get_ball_speed(ball)

    angle += random.uniform(-amount, amount)

    ball["vx"] = math.cos(angle) * speed
    ball["vy"] = math.sin(angle) * speed

    clamp_ball_speed(ball)

# =====================================
# ========= 13. 粒子系统 =========
# =====================================
particles = []
MAX_PARTICLES = 180

def spawn_particles(x, y, color=(255, 200, 120), count=12, speed_scale=1.0, life_bias=0):
    """
    生成粒子

    最终调参版进一步压低粒子总量，
    让画面更干净、高潮更明显。
    """
    if len(particles) >= MAX_PARTICLES:
        return

    available = MAX_PARTICLES - len(particles)
    real_count = min(count, available)

    for _ in range(real_count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.0, 2.6) * speed_scale

        particles.append({
            "x": x,
            "y": y,
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "life": random.randint(14, 28) + life_bias,
            "color": color
        })

def update_particles():
    """
    更新粒子
    """
    for particle in particles[:]:
        particle["x"] += particle["vx"]
        particle["y"] += particle["vy"]
        particle["life"] -= 1

        particle["vx"] *= 0.982
        particle["vy"] *= 0.982

        if particle["life"] <= 0:
            particles.remove(particle)

def draw_particles(surface, camera_offset_x=0, camera_offset_y=0):
    """
    绘制粒子
    """
    for particle in particles:
        pygame.draw.circle(
            surface,
            particle["color"],
            (int(particle["x"] + camera_offset_x), int(particle["y"] + camera_offset_y)),
            2
        )

# =====================================
# ========= 14. 冲击波系统 =========
# =====================================
shockwaves = []

def spawn_shockwave(x, y, color=(255, 220, 180), max_radius=75, growth=3.8):
    """
    生成冲击波
    主要用于逃出事件
    """
    shockwaves.append({
        "x": x,
        "y": y,
        "radius": 8,
        "max_radius": max_radius,
        "growth": growth,
        "life": 18,
        "color": color
    })

def update_shockwaves():
    """
    更新冲击波
    """
    for wave in shockwaves[:]:
        wave["radius"] += wave["growth"]
        wave["life"] -= 1

        if wave["life"] <= 0 or wave["radius"] >= wave["max_radius"]:
            shockwaves.remove(wave)

def draw_shockwaves(surface, camera_offset_x=0, camera_offset_y=0):
    """
    绘制冲击波
    """
    for wave in shockwaves:
        alpha_ratio = max(0.0, wave["life"] / 18.0)
        width = max(1, int(2 + alpha_ratio))

        pygame.draw.circle(
            surface,
            wave["color"],
            (int(wave["x"] + camera_offset_x), int(wave["y"] + camera_offset_y)),
            int(wave["radius"]),
            width
        )

# =====================================
# ========= 15. 屏幕震动系统 =========
# =====================================
screen_shake_timer = 0
screen_shake_strength = 0

def trigger_screen_shake(strength=4, duration=6):
    """
    触发屏幕震动
    只用于高潮事件，并保持克制
    """
    global screen_shake_timer, screen_shake_strength
    screen_shake_timer = duration
    screen_shake_strength = strength

def update_screen_shake():
    """
    更新屏幕震动
    """
    global screen_shake_timer
    if screen_shake_timer > 0:
        screen_shake_timer -= 1

def get_camera_offset():
    """
    获取当前镜头偏移量
    """
    if screen_shake_timer <= 0:
        return 0, 0

    offset_x = random.randint(-screen_shake_strength, screen_shake_strength)
    offset_y = random.randint(-screen_shake_strength, screen_shake_strength)
    return offset_x, offset_y

# =====================================
# ========= 16. 事件特效分级 =========
# =====================================
def trigger_ball_escape(ball):
    """
    触发单个小球逃出

    最终调参版：
    - 保持最强事件定位
    - 但让强度更集中、更清楚
    """
    if ball["escaped"]:
        return

    ball["escaped"] = True

    pulse = get_global_pulse()
    count = 38 + int(16 * pulse)

    spawn_particles(
        ball["x"],
        ball["y"],
        ball["color"],
        count=count,
        speed_scale=1.55,
        life_bias=8
    )

    shock_color = (
        min(255, ball["color"][0] + 20),
        min(255, ball["color"][1] + 20),
        min(255, ball["color"][2] + 20),
    )
    spawn_shockwave(ball["x"], ball["y"], shock_color, max_radius=78, growth=3.8)
    trigger_screen_shake(strength=4, duration=6)

def spawn_layer_transition_effect(ball):
    """
    穿层时触发轻粒子提示
    """
    count = 1 + int(2 * get_global_pulse())
    spawn_particles(
        ball["x"],
        ball["y"],
        ball["color"],
        count=count,
        speed_scale=0.5,
        life_bias=-5
    )

# =====================================
# ========= 17. 小球碰撞圆环反弹系统 =========
# =====================================
def reflect_outer(ball, ring):
    """
    处理某个小球撞到当前层外边界的反弹
    """
    dx, dy = get_dxdy(ball)
    distance = math.sqrt(dx * dx + dy * dy)
    if distance == 0:
        distance = 0.001

    nx = dx / distance
    ny = dy / distance

    dot = ball["vx"] * nx + ball["vy"] * ny

    ball["vx"] = ball["vx"] - 2 * dot * nx
    ball["vy"] = ball["vy"] - 2 * dot * ny

    ball["x"] = center_x + nx * (ring["radius"] - ball["radius"])
    ball["y"] = center_y + ny * (ring["radius"] - ball["radius"])

    # 普通撞墙：进一步降噪
    count = 2 + int(1 * get_global_pulse())
    spawn_particles(ball["x"], ball["y"], ball["color"], count=count, speed_scale=0.65, life_bias=-7)

    add_angular_noise(ball, amount=0.04)

def reflect_inner(ball, ring):
    """
    处理某个小球撞到当前层内边界的反弹
    """
    dx, dy = get_dxdy(ball)
    distance = math.sqrt(dx * dx + dy * dy)
    if distance == 0:
        distance = 0.001

    nx = -dx / distance
    ny = -dy / distance

    dot = ball["vx"] * nx + ball["vy"] * ny

    ball["vx"] = ball["vx"] - 2 * dot * nx
    ball["vy"] = ball["vy"] - 2 * dot * ny

    raw_nx = dx / distance
    raw_ny = dy / distance
    safe_radius = ring["radius"] + ball["radius"]

    ball["x"] = center_x + raw_nx * safe_radius
    ball["y"] = center_y + raw_ny * safe_radius

    count = 2 + int(1 * get_global_pulse())
    spawn_particles(ball["x"], ball["y"], ball["color"], count=count, speed_scale=0.65, life_bias=-7)

    add_angular_noise(ball, amount=0.04)

# =====================================
# ========= 18. 单球核心更新 =========
# =====================================
def update_one_ball(ball):
    """
    更新一个小球的逻辑
    """
    if ball["escaped"]:
        return

    local_pulse = math.sin(rhythm * 2.1 + ball["pulse_offset"])
    speed_factor = 1.0 + 0.10 * math.sin(rhythm) + 0.07 * local_pulse

    ball["x"] += ball["vx"] * speed_factor
    ball["y"] += ball["vy"] * speed_factor

    layer = ball["layer"]
    distance = get_dist(ball)
    angle = get_angle(ball)

    outer_ring = rings[layer]
    outer_limit = outer_ring["radius"] - ball["radius"]

    if distance >= outer_limit:
        if layer < len(rings) - 1:
            if is_angle_in_gap(angle, outer_ring):
                ball["layer"] += 1
                spawn_layer_transition_effect(ball)
                return
            else:
                reflect_outer(ball, outer_ring)
                return
        else:
            if is_angle_in_gap(angle, outer_ring):
                trigger_ball_escape(ball)
                return
            else:
                reflect_outer(ball, outer_ring)
                return

    if layer > 0:
        inner_ring = rings[layer - 1]
        inner_limit = inner_ring["radius"] + ball["radius"]

        if distance <= inner_limit:
            if is_angle_in_gap(angle, inner_ring):
                ball["layer"] -= 1
                spawn_layer_transition_effect(ball)
                return
            else:
                reflect_inner(ball, inner_ring)
                return

    if ball["layer"] == ball["last_layer"]:
        ball["layer_timer"] += 1
    else:
        ball["layer_timer"] = 0
        ball["last_layer"] = ball["layer"]

    if ball["layer_timer"] > 120:
        rad = math.radians(angle)
        ball["vx"] += math.cos(rad) * 0.16
        ball["vy"] += math.sin(rad) * 0.16
        clamp_ball_speed(ball)

# =====================================
# ========= 19. 球球碰撞系统 =========
# =====================================
def collide_two_balls(ball_a, ball_b):
    """
    处理两个小球的碰撞
    只处理同层球
    """
    if ball_a["layer"] != ball_b["layer"]:
        return

    dx = ball_b["x"] - ball_a["x"]
    dy = ball_b["y"] - ball_a["y"]
    distance = math.sqrt(dx * dx + dy * dy)

    min_dist = ball_a["radius"] + ball_b["radius"]

    if distance >= min_dist:
        return

    if distance == 0:
        dx = random.uniform(-0.1, 0.1)
        dy = random.uniform(-0.1, 0.1)
        distance = math.sqrt(dx * dx + dy * dy)
        if distance == 0:
            distance = 0.001

    nx = dx / distance
    ny = dy / distance

    overlap = min_dist - distance

    ball_a["x"] -= nx * (overlap / 2)
    ball_a["y"] -= ny * (overlap / 2)
    ball_b["x"] += nx * (overlap / 2)
    ball_b["y"] += ny * (overlap / 2)

    tx = -ny
    ty = nx

    v1n = ball_a["vx"] * nx + ball_a["vy"] * ny
    v1t = ball_a["vx"] * tx + ball_a["vy"] * ty

    v2n = ball_b["vx"] * nx + ball_b["vy"] * ny
    v2t = ball_b["vx"] * tx + ball_b["vy"] * ty

    new_v1n = v2n
    new_v2n = v1n

    ball_a["vx"] = tx * v1t + nx * new_v1n
    ball_a["vy"] = ty * v1t + ny * new_v1n

    ball_b["vx"] = tx * v2t + nx * new_v2n
    ball_b["vy"] = ty * v2t + ny * new_v2n

    add_angular_noise(ball_a, amount=0.035)
    add_angular_noise(ball_b, amount=0.035)

    clamp_ball_speed(ball_a)
    clamp_ball_speed(ball_b)

    impact_x = (ball_a["x"] + ball_b["x"]) / 2
    impact_y = (ball_a["y"] + ball_b["y"]) / 2

    mix_color = (
        (ball_a["color"][0] + ball_b["color"][0]) // 2,
        (ball_a["color"][1] + ball_b["color"][1]) // 2,
        (ball_a["color"][2] + ball_b["color"][2]) // 2,
    )

    # 球球碰撞：保留存在感，但更短、更干净
    count = 3 + int(2 * get_global_pulse())
    spawn_particles(impact_x, impact_y, mix_color, count=count, speed_scale=0.85, life_bias=-3)

def handle_ball_collisions():
    """
    统一处理所有小球之间的碰撞
    """
    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            ball_a = balls[i]
            ball_b = balls[j]

            if ball_a["escaped"] or ball_b["escaped"]:
                continue

            collide_two_balls(ball_a, ball_b)

# =====================================
# ========= 20. 多球总更新 =========
# =====================================
def update_balls():
    """
    更新所有小球
    先处理球与圆环，再处理球与球
    """
    for ball in balls:
        update_one_ball(ball)

    handle_ball_collisions()

# =====================================
# ========= 21. 圆环更新 =========
# =====================================
def update_rings():
    """
    更新圆环缺口旋转
    最终调参版略微降低旋转躁动感
    """
    for i, ring in enumerate(rings):
        speed = ring["base_speed"] * (1 + 0.55 * math.sin(rhythm + i * 0.85))
        ring["gap_start"] = (ring["gap_start"] + speed) % 360
        ring["gap_end"] = (ring["gap_end"] + speed) % 360

# =====================================
# ========= 22. 绘制系统 =========
# =====================================
def draw_background():
    """
    绘制带轻微呼吸感的背景
    """
    bg_value = 6 + int(6 * get_global_pulse())
    screen.fill((bg_value, bg_value, bg_value))

def draw_rings(surface, camera_offset_x=0, camera_offset_y=0):
    """
    绘制所有圆环
    """
    layer_has_ball = [False] * len(rings)
    for ball in balls:
        if not ball["escaped"]:
            layer_has_ball[ball["layer"]] = True

    for i, ring in enumerate(rings):
        ring_pulse = abs(math.sin(rhythm + i * 0.75))
        intensity = 100 + int(80 * ring_pulse)
        color = (intensity, intensity, intensity)

        if layer_has_ball[i]:
            boost = 28 + int(16 * get_global_pulse())
            bright = min(255, intensity + boost)
            color = (bright, bright, bright)

        for angle in range(0, 360, 2):
            if not is_angle_in_gap(angle, ring):
                rad = math.radians(angle)
                x = int(center_x + ring["radius"] * math.cos(rad) + camera_offset_x)
                y = int(center_y + ring["radius"] * math.sin(rad) + camera_offset_y)
                pygame.draw.circle(surface, color, (x, y), 2)

def draw_balls(surface, camera_offset_x=0, camera_offset_y=0):
    """
    绘制所有未逃出的小球
    """
    for ball in balls:
        if ball["escaped"]:
            continue

        pulse = 1 + 0.20 * abs(math.sin(rhythm * 2.6 + ball["pulse_offset"]))
        radius = int(ball["radius"] * pulse)

        pygame.draw.circle(
            surface,
            ball["color"],
            (int(ball["x"] + camera_offset_x), int(ball["y"] + camera_offset_y)),
            radius
        )

def draw_ui(surface):
    """
    绘制简单文字信息
    """
    alive_count = 0
    for ball in balls:
        if not ball["escaped"]:
            alive_count += 1

    round_text = font.render(f"Round: {current_round}", True, (230, 230, 230))
    alive_text = small_font.render(f"Balls Left: {alive_count}", True, (190, 190, 190))

    surface.blit(round_text, (20, 20))
    surface.blit(alive_text, (20, 50))

# =====================================
# ========= 23. 总重置系统 =========
# =====================================
def full_reset():
    """
    完整重置
    """
    global current_round, round_clear_timer, screen_shake_timer, screen_shake_strength

    current_round = 1
    round_clear_timer = 0
    screen_shake_timer = 0
    screen_shake_strength = 0
    reset_round()

full_reset()

# =====================================
# ========= 24. 主循环 =========
# =====================================
while True:

    # ========= 24.1 事件处理 =========
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                full_reset()

    # ========= 24.2 更新 =========
    update_rhythm()
    update_rings()
    update_balls()
    update_particles()
    update_shockwaves()
    update_screen_shake()

    # ---------- 24.2.1 检查是否整轮结束 ----------
    if all_balls_escaped():
        round_clear_timer += 1

        if round_clear_timer >= ROUND_CLEAR_DELAY:
            current_round += 1
            round_clear_timer = 0
            reset_round()
    else:
        round_clear_timer = 0

    # ========= 24.3 绘制 =========
    camera_offset_x, camera_offset_y = get_camera_offset()

    draw_background()
    screen.blit(fade_surface, (0, 0))

    draw_rings(screen, camera_offset_x, camera_offset_y)
    draw_shockwaves(screen, camera_offset_x, camera_offset_y)
    draw_particles(screen, camera_offset_x, camera_offset_y)
    draw_balls(screen, camera_offset_x, camera_offset_y)
    draw_ui(screen)

    pygame.display.flip()
    clock.tick(60)