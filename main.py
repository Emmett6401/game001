import pygame
import random
import sys

# 초기화
pygame.init()

# 화면 크기 설정
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("우주선 vs 혜성")

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# 사운드 초기화 및 로드
pygame.mixer.init()
comet_pass_sound = pygame.mixer.Sound("d:\\2025_AI\\prjt002\\sounds\\comet_pass.wav")  # 혜성 스칠 때 사운드
comet_hit_sound = pygame.mixer.Sound("d:\\2025_AI\\prjt002\\sounds\\comet_hit.wav")  # 혜성 맞을 때 사운드 추가

# 기존 사운드 재활용
spaceship_explosion_sound = comet_hit_sound  # 비행기 폭발 소리로 재활용
spaceship_explosion_sound.set_volume(0.7)  # 볼륨 조정

bullet_fire_sound = comet_pass_sound  # 총알 발사 소리로 재활용
bullet_fire_sound.set_volume(0.5)  # 볼륨 조정

# 이미지 로드
spaceship_image = pygame.image.load("d:\\2025_AI\\prjt002\\images\\ship.png")  # 우주선 이미지
comet_images = [
    pygame.image.load(f"d:\\2025_AI\\prjt002\\images\\comet{i}.png") for i in range(1, 13)
]  # 혜성 이미지 1~12

# 우주선 클래스
class Spaceship:
    def __init__(self):
        self.image = pygame.transform.scale(spaceship_image, (50, 50))  # 우주선 크기 조정
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.speed = 5

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# 혜성 클래스
class Comet:
    def __init__(self, speed_multiplier=1):
        self.images = [pygame.transform.scale(img, (random.randint(20, 50), random.randint(20, 50))) for img in comet_images]  # 랜덤 크기로 모든 이미지 로드
        self.current_frame = 0  # 현재 애니메이션 프레임
        self.animation_speed = 0.2  # 애니메이션 속도 (프레임당 증가값)
        self.image = self.images[self.current_frame]
        self.rect = self.image.get_rect(center=(random.randint(0, SCREEN_WIDTH), 0))
        self.speed = random.randint(3, 7) * speed_multiplier  # 속도 증가 반영

    def move(self):
        self.rect.y += self.speed
        self.current_frame += self.animation_speed  # 프레임 업데이트
        if self.current_frame >= len(self.images):  # 프레임 순환
            self.current_frame = 0
        self.image = self.images[int(self.current_frame)]  # 현재 프레임 이미지 설정

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# 총알 클래스
class Bullet:
    def __init__(self, x, y):
        self.image = pygame.Surface((5, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -10  # 총알은 위로 이동

    def move(self):
        self.rect.y += self.speed

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# 별 클래스
class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.randint(1, 3)  # 별의 속도
        self.size = random.randint(1, 3)  # 별의 크기

    def move(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:  # 화면 아래로 나가면 다시 위로 생성
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (self.x, self.y), self.size)

def show_message(screen, font, message, sub_message):
    """게임 화면에 메시지 박스를 표시"""
    screen.fill(BLACK)
    message_text = font.render(message, True, WHITE)
    sub_message_text = font.render(sub_message, True, WHITE)
    screen.blit(message_text, (SCREEN_WIDTH // 2 - message_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(sub_message_text, (SCREEN_WIDTH // 2 - sub_message_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
    pygame.display.flip()

    # 사용자 입력 대기
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # R 키로 재시작
                    return True
                if event.key == pygame.K_q:  # Q 키로 종료
                    return False

# 게임 루프
def main():
    clock = pygame.time.Clock()
    spaceship = Spaceship()
    comets = []
    bullets = []  # 총알 리스트 추가
    stars = [Star() for _ in range(100)]  # 별 생성
    score = 0
    font = pygame.font.Font(None, 36)
    speed_multiplier = 1  # 혜성 속도 증가를 위한 변수
    game_duration = 60  # 게임 시간 제한 (초)
    start_ticks = pygame.time.get_ticks()  # 게임 시작 시간
    max_bullets = 200  # 총알 최대 개수
    remaining_bullets = max_bullets  # 남은 총알 개수
    lives = 3  # 플레이어 목숨

    while True:
        screen.fill(BLACK)

        # 별 이동 및 그리기
        for star in stars:
            star.move()
            star.draw(screen)

        # 남은 시간 계산
        elapsed_time = (pygame.time.get_ticks() - start_ticks) / 1000  # 경과 시간 (초)
        remaining_time = max(0, game_duration - elapsed_time)  # 남은 시간
        if remaining_time <= 0:
            print("Time's up! Final Score:", score)
            pygame.time.wait(500)  # 짧은 대기 후 메시지 박스 표시

            # 게임 화면에 메시지 박스 표시
            if show_message(screen, font, "Time's Up!", f"Final Score: {score}\nPress R to Restart or Q to Quit"):
                main()  # 게임 재시작
            else:
                pygame.quit()
                sys.exit()

        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and remaining_bullets > 0:  # 스페이스바로 총알 발사
                    bullets.append(Bullet(spaceship.rect.centerx, spaceship.rect.top))
                    remaining_bullets -= 1  # 총알 개수 감소
                    bullet_fire_sound.play()  # 총알 발사 소리 재생

        # 키 입력 처리
        keys = pygame.key.get_pressed()
        spaceship.move(keys)

        # 총알 이동 및 화면 밖 제거
        for bullet in bullets[:]:
            bullet.move()
            if bullet.rect.bottom < 0:  # 화면 위로 나가면 제거
                bullets.remove(bullet)

        # 혜성 생성
        if random.randint(1, 30) == 1:
            comets.append(Comet(speed_multiplier))

        # 혜성 이동 및 충돌 처리
        for comet in comets[:]:
            comet.move()
            if comet.rect.top > SCREEN_HEIGHT:
                comets.remove(comet)
                comet_pass_sound.play()  # 혜성이 화면을 벗어날 때 사운드 재생

            # 총알과 혜성 충돌 처리
            for bullet in bullets[:]:
                if bullet.rect.colliderect(comet.rect):
                    comets.remove(comet)
                    bullets.remove(bullet)
                    score += 5  # 혜성 제거 시 추가 점수
                    print(f"Comet destroyed! Current score: {score}")

                    # 혜성 크기에 따라 사운드 길이 조정
                    comet_size = comet.rect.width
                    sound_length = max(100, 500 - comet_size * 10)  # 최소 100ms, 최대 500ms
                    comet_hit_sound.play(maxtime=sound_length)  # 사운드 재생 시간 제한
                    break  # 충돌한 혜성만 제거

            if comet.rect.colliderect(spaceship.rect):
                lives -= 1  # 목숨 감소
                print(f"Lives remaining: {lives}")
                spaceship_explosion_sound.play()  # 비행기 폭발 소리 재생
                comets.remove(comet)  # 충돌한 혜성 제거

                if lives <= 0:  # 목숨이 0이 되면 게임 종료
                    print("Game Over! Final Score:", score)
                    pygame.time.wait(500)  # 짧은 대기 후 메시지 박스 표시

                    # 게임 화면에 메시지 박스 표시
                    if show_message(screen, font, "Game Over!", "Press R to Restart or Q to Quit"):
                        main()  # 게임 재시작
                    else:
                        pygame.quit()
                        sys.exit()

        # 점수에 따라 난이도 증가
        if score > 0 and score % 10 == 0:  # 10점마다 속도 증가
            speed_multiplier += 0.1
            score += 1  # 중복 증가 방지

        # 그리기
        spaceship.draw(screen)
        for comet in comets:
            comet.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)

        # 점수, 남은 시간, 남은 총알 및 목숨 표시
        score_text = font.render(f"Score: {score}", True, WHITE)
        time_text = font.render(f"Time: {int(remaining_time)}s", True, WHITE)
        bullets_text = font.render(f"Bullets: {remaining_bullets}/{max_bullets}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(time_text, (SCREEN_WIDTH - 150, 10))  # 화면 오른쪽 상단에 남은 시간 표시
        screen.blit(bullets_text, (10, 40))  # 화면 왼쪽 상단에 남은 총알 표시
        screen.blit(lives_text, (10, 70))  # 화면 왼쪽 상단에 남은 목숨 표시

        # 화면 업데이트
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
