import flet as ft
from flet import BoxShadow, Offset
import random
import asyncio
import json
import os
from datetime import datetime
from assets.styles.styles import *
from appdirs import user_data_dir

class SnakeGame:
    def __init__(self, page: ft.Page):
        # Create app data directory
        self.app_data_dir = user_data_dir("SnakeGame", "Hahelui")
        os.makedirs(self.app_data_dir, exist_ok=True)
        
        self.page = page
        self.page.title = "Snake Game Flet - By: @Hahelui"
        self.page.window_width = BOARD_SIZE + 200
        self.page.window_height = BOARD_SIZE + 300
        self.page.window_resizable = False
        self.page.padding = 0
        self.page.bgcolor = BACKGROUND_COLOR
        
        # Audio setup
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.eat_sound = ft.Audio(src=os.path.join(base_path, "assets/sounds/eat.wav"))
        self.music = ft.Audio(
            src=os.path.join(base_path, "assets/sounds/music.wav"),
            autoplay=True,
            release_mode=ft.audio.ReleaseMode.LOOP
        )
        self.music2 = ft.Audio(
            src=os.path.join(base_path, "assets/sounds/music2.wav"),
            release_mode=ft.audio.ReleaseMode.LOOP
        )
        self.pause_sound = ft.Audio(src=os.path.join(base_path, "assets/sounds/pause.wav"))
        self.page.overlay.extend([self.eat_sound, self.music, self.music2, self.pause_sound])
        
        # Game settings
        self.queued_direction = None
        self.paused = False
        self.special_food_timer = 0
        self.special_food_duration = 4
        self.show_scores_card = False
        self.last_food_move = 0  # Track last food movement time
        
        # High scores
        self.high_scores_file = os.path.join(self.app_data_dir, "high_scores.json")
        self.settings_file = os.path.join(self.app_data_dir, "settings.json")
        self.high_scores = self.load_high_scores()
        self.load_settings()
        
        # Set initial game speed from saved settings
        speed_pct = self.saved_speed_value
        self.speed = MIN_SPEED - (speed_pct / 100) * (MIN_SPEED - MAX_SPEED)
        self.speed = max(MAX_SPEED, min(MIN_SPEED, self.speed))
        
        # Initialize game state
        self.snake = [(GRID_SIZE // 2, GRID_SIZE // 2)]
        self.direction = (1, 0)
        self.score = 0
        self.game_over = False
        self.food = None
        self.food_type = "normal"
        self.food_direction = (0, 0)  # Direction for special food movement
        self.running = True
        
        # Start background music loop
        asyncio.create_task(self.loop_background_music())
        
        # Calculate initial slider value based on default speed
        initial_speed_pct = (MIN_SPEED - DEFAULT_SPEED) / (MIN_SPEED - MAX_SPEED) * 100
        
        # Create game board
        self.board = ft.Container(
            content=ft.Stack([]),
            width=BOARD_SIZE,
            height=BOARD_SIZE,
            bgcolor=BACKGROUND_COLOR,
            border_radius=BOARD_BORDER_RADIUS,
            border=ft.border.all(1, BORDER_COLOR),
            shadow=BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.colors.with_opacity(0.15, ft.Colors.BLACK),
                offset=Offset(0, 5),
            ),
            padding=BOARD_PADDING,
        )
        
        # Score display with animation
        self.score_text = ft.Text(
            f"Score: {self.score}",
            **SCORE_STYLE,
            animate_scale=SCORE_ANIMATION,
        )
        
        # High score text with button
        self.high_score_text = ft.Text(
            f"High Score: {self.get_highest_score()}",
            **SCORE_STYLE
        )
        high_score_row = ft.Row(
            [
                self.high_score_text,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5,
        )

        # High scores card
        self.scores_card = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("High Scores", **CARD_TITLE_STYLE),
                            ft.IconButton(
                                icon=ft.icons.CLOSE,
                                on_click=lambda _: self.toggle_scores_card(),
                                **CLOSE_BUTTON_STYLE,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(height=1, color=GRID_COLOR),
                    ft.Column(
                        [ft.Text(self.show_high_scores(), **SCORES_LIST_STYLE)],
                        scroll=ft.ScrollMode.AUTO,
                        spacing=10,
                    ),
                ],
                tight=True,
                spacing=15,
            ),
            width=300,
            visible=False,
            **CARD_STYLE,
        )
        
        # Title
        self.title = ft.Text(
            "Snake Game Flet - By: @Hahelui",
            **TITLE_STYLE
        )
        
        # Speed control container
        speed_text = ft.Text("Speed", **CONTROLS_STYLE)
        self.speed_slider = ft.Slider(
            min=0,
            max=100,
            value=self.saved_speed_value,  # Use saved speed
            on_change=self.update_speed,
            width=150,
        )

        # Volume control
        volume_text = ft.Text("Volume", **CONTROLS_STYLE)
        self.volume_slider = ft.Slider(
            min=0,
            max=100,
            value=self.saved_volume_value,  # Use saved volume
            on_change=self.update_volume,
            width=150,
        )
        # Set initial volume
        self.music.volume = self.saved_volume_value / 100
        self.music2.volume = self.saved_volume_value / 100
        
        # Create a row for the pause menu buttons
        scores_button = ft.IconButton(
            icon=ft.icons.LEADERBOARD,
            icon_color=SCORE_COLOR,
            icon_size=24,
            tooltip="Show High Scores",
            on_click=lambda _: self.toggle_scores_card(),
        )
        
        self.speed_container = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [speed_text, self.speed_slider],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=5,
                    ),
                    ft.VerticalDivider(width=1, color=GRID_COLOR),
                    ft.Column(
                        [volume_text, self.volume_slider],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=5,
                    ),
                    ft.VerticalDivider(width=1, color=GRID_COLOR),
                    scores_button,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
            visible=False,
            padding=20,
        )
        
        # Set page as focused control
        self.page.focused_control = self.page
        
        # Game status text (Paused/Game Over)
        self.status_text = ft.Text(
            "PAUSED",
            visible=False,
            color=GAME_OVER_COLOR,
            size=24,
            weight="bold",
        )
        
        # Game over text
        self.game_over_text = ft.Text(
            "Game Over!",
            visible=False,
            **GAME_OVER_STYLE
        )

        # Instructions
        self.instructions = ft.Text(
            "Press SPACE to play again",
            visible=False,
            **INSTRUCTION_STYLE
        )
        
        # Controls text
        movement_controls = self.create_key_text("↑/W, ↓/S, ←/A, →/D")
        space_control = self.create_key_text("SPACE")
        
        controls_text = ft.Row(
            [
                ft.Text("Movement: ", **CONTROLS_STYLE),
                movement_controls,
                ft.Text(" | ", **CONTROLS_STYLE),
                ft.Text("Pause/Restart: ", **CONTROLS_STYLE),
                space_control,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        
        # Layout
        self.page.add(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=self.title,
                            alignment=ft.alignment.center,
                            padding=ft.padding.only(top=20, bottom=10),
                        ),
                        ft.Container(
                            content=self.score_text,
                            alignment=ft.alignment.center,
                            padding=ft.padding.only(bottom=10),
                        ),
                        ft.Container(
                            content=high_score_row,
                            alignment=ft.alignment.center,
                            padding=ft.padding.only(bottom=10),
                        ),
                        ft.Container(
                            content=controls_text,
                            alignment=ft.alignment.center,
                            padding=ft.padding.only(bottom=20),
                        ),
                        ft.Container(
                            content=ft.Stack(
                                [
                                    self.board,
                                    self.scores_card,
                                    ft.Container(
                                        content=self.status_text,
                                        alignment=ft.alignment.center,
                                        width=BOARD_SIZE,
                                        height=BOARD_SIZE,
                                    ),
                                ],
                                expand=True,
                            ),
                            alignment=ft.alignment.center,
                        ),
                        ft.Container(
                            content=ft.Column(
                                [
                                    self.game_over_text,
                                    self.instructions
                                ],
                                spacing=5,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            alignment=ft.alignment.center,
                            padding=ft.padding.only(top=20, bottom=10),
                        ),
                        self.speed_container,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.top_center,
            )
        )
        
        # Key event handler
        self.page.on_keyboard_event = self.handle_keyboard_event
        
        # Start game
        self.spawn_food()
    
    def create_key_text(self, text):
        return ft.Container(
            content=ft.Text(text, **KEY_TEXT_STYLE),
            **KEY_CONTAINER_STYLE
        )
    
    def update_speed(self, e):
        """Update game speed based on slider value"""
        speed_pct = e.control.value
        self.speed = MIN_SPEED - (speed_pct / 100) * (MIN_SPEED - MAX_SPEED)
        self.speed = max(MAX_SPEED, min(MIN_SPEED, self.speed))
        self.save_settings()
        self.page.update()
    
    def update_volume(self, e):
        """Update music volume based on slider value"""
        volume = e.control.value / 100  # Convert percentage to decimal (0-1)
        self.music.volume = volume
        self.music2.volume = volume
        self.save_settings()
    
    def spawn_food(self):
        """Spawn new food at random location"""
        while True:
            x = random.randint(0, GRID_SIZE - 1)
            y = random.randint(0, GRID_SIZE - 1)
            if (x, y) not in self.snake:
                self.food = (x, y)
                # 80% chance for special food
                self.food_type = "special" if random.random() < 0.05 else "normal"
                if self.food_type == "special":
                    self.special_food_timer = 0  # Reset timer for special food
                    # Random direction for special food
                    self.food_direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
                    self.last_food_move = 0
                else:
                    self.food_direction = (0, 0)
                break
    
    def is_valid_direction(self, new_dir, current_dir):
        return not (new_dir[0] == -current_dir[0] and new_dir[1] == -current_dir[1])
    
    def toggle_pause(self):
        """Toggle game pause state"""
        if not self.game_over:
            self.paused = not self.paused
            self.status_text.visible = self.paused
            self.speed_container.visible = self.paused
            self.pause_sound.play()
            
            # Pause/resume music based on game state
            if self.paused:
                if self.food_type == "special":
                    self.music2.pause()
                else:
                    self.music.pause()
            else:
                if self.food_type == "special":
                    self.music2.resume()
                else:
                    self.music.resume()
                    
            self.page.update()
    
    def handle_keyboard_event(self, e: ft.KeyboardEvent):
        """Handle keyboard events for game control"""
        if e.key == "P":
            self.toggle_pause()
        elif e.key == " ":  # Space key
            if self.game_over:

                self.reset_game()
            else:
                self.toggle_pause()
        elif not self.paused and not self.game_over:
            # Only handle direction changes if game is running
            if e.key == "Arrow Left" and self.direction[0] != 1:
                self.queued_direction = (-1, 0)
            elif e.key == "Arrow Right" and self.direction[0] != -1:
                self.queued_direction = (1, 0)
            elif e.key == "Arrow Up" and self.direction[1] != 1:
                self.queued_direction = (0, -1)
            elif e.key == "Arrow Down" and self.direction[1] != -1:
                self.queued_direction = (0, 1)
    
    def reset_game(self):
        if self.game_over:
            # Update high scores before resetting
            self.update_high_scores()
        
        self.snake = [(GRID_SIZE // 2, GRID_SIZE // 2)]
        self.direction = (1, 0)
        self.score = 0
        self.game_over = False
        self.food = None
        self.food_type = "normal"
        self.food_direction = (0, 0)
        self.running = True
        self.paused = False
        
        # Reset game speed from saved settings
        speed_pct = self.speed_slider.value
        self.speed = MIN_SPEED - (speed_pct / 100) * (MIN_SPEED - MAX_SPEED)
        self.speed = max(MAX_SPEED, min(MIN_SPEED, self.speed))
        
        # Reset UI elements
        self.game_over_text.visible = False
        self.instructions.visible = False
        self.status_text.visible = False
        self.speed_container.visible = False
        self.scores_card.visible = False
        self.score_text.value = f"Score: {self.score}"
        self.score_text.scale = 1
        self.spawn_food()
        self.redraw_board()
        self.page.update()
    
    def get_cell_position(self, grid_x, grid_y):
        x = grid_x * (CELL_SIZE + CELL_SPACING)
        y = grid_y * (CELL_SIZE + CELL_SPACING)
        return x, y
    
    def move_special_food(self):
        """Move special food in its current direction"""
        if self.food_type == "special":
            new_x = (self.food[0] + self.food_direction[0]) % GRID_SIZE
            new_y = (self.food[1] + self.food_direction[1]) % GRID_SIZE
            
            # If new position collides with snake, reverse direction
            if (new_x, new_y) in self.snake:
                self.food_direction = (-self.food_direction[0], -self.food_direction[1])
                new_x = (self.food[0] + self.food_direction[0]) % GRID_SIZE
                new_y = (self.food[1] + self.food_direction[1]) % GRID_SIZE
            
            self.food = (new_x, new_y)
    
    async def game_loop(self):
        """Main game loop"""
        self.running = True
        while self.running:
            if not self.paused and not self.game_over:
                # Update snake position
                if self.queued_direction and self.is_valid_direction(self.queued_direction, self.direction):
                    self.direction = self.queued_direction
                    self.queued_direction = None
                
                # Move special food at half snake speed
                if self.food_type == "special":
                    self.last_food_move += self.speed
                    if self.last_food_move >= self.speed * 2:  # Move at half speed
                        self.move_special_food()
                        self.last_food_move = 0
                
                # Calculate new head position
                new_head = (
                    (self.snake[0][0] + self.direction[0]) % GRID_SIZE,
                    (self.snake[0][1] + self.direction[1]) % GRID_SIZE
                )
                
                # Check for collision with self
                if new_head in self.snake:
                    self.game_over = True
                    self.game_over_text.visible = True
                    self.instructions.visible = True
                    self.pause_sound.play()
                    # Update and show high scores
                    self.update_high_scores()
                    self.scores_card.content.controls[2].controls[0].value = self.show_high_scores()
                    self.scores_card.visible = True
                    self.page.update()
                    continue
                
                # Move snake
                self.snake.insert(0, new_head)
                
                # Check for food collision
                ate_food = False
                if new_head == self.food:
                    self.eat_food()
                    ate_food = True
                
                if not ate_food:
                    self.snake.pop()
                
                # Update special food timer
                if self.food_type == "special":
                    self.special_food_timer += self.speed
                    if self.special_food_timer >= self.special_food_duration:
                        self.spawn_food()  # Replace with new food
                
                # Clear and redraw board
                self.redraw_board()
            
            # Wait before next frame
            await asyncio.sleep(self.speed)
    
    def eat_food(self):
        self.snake.append(self.food)
        self.score += 10 if self.food_type == "normal" else 30
        self.score_text.value = f"Score: {self.score}"
        self.score_text.scale = 1.2
        self.eat_sound.play()
        self.page.update(self.score_text)
        self.spawn_food()
    
    def redraw_board(self):
        """Redraw the game board with current state"""
        board_content = []
        
        # Draw grid
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                cell = ft.Container(
                    width=CELL_SIZE,
                    height=CELL_SIZE,
                    left=x * (CELL_SIZE + CELL_SPACING),
                    top=y * (CELL_SIZE + CELL_SPACING),
                    bgcolor=BOARD_COLOR,
                    border_radius=CELL_BORDER_RADIUS,
                )
                board_content.append(cell)
        
        # Draw food
        if self.food:
            if self.food_type == "special":
                # Calculate opacity based on timer
                opacity = max(0.3, 1 - (self.special_food_timer / self.special_food_duration))
                food = ft.Container(
                    width=CELL_SIZE,
                    height=CELL_SIZE,
                    left=self.food[0] * (CELL_SIZE + CELL_SPACING),
                    top=self.food[1] * (CELL_SIZE + CELL_SPACING),
                    bgcolor=SPECIAL_FOOD_COLOR,
                    border_radius=CELL_BORDER_RADIUS,
                    border=ft.border.all(2, SPECIAL_FOOD_OUTLINE_COLOR),
                    opacity=opacity,
                    animate=FOOD_ANIMATION,
                )
            else:
                food = ft.Container(
                    width=CELL_SIZE,
                    height=CELL_SIZE,
                    left=self.food[0] * (CELL_SIZE + CELL_SPACING),
                    top=self.food[1] * (CELL_SIZE + CELL_SPACING),
                    bgcolor=FOOD_COLOR,
                    border_radius=CELL_BORDER_RADIUS,
                    border=FOOD_BORDER,
                    animate=FOOD_ANIMATION,
                )
            board_content.append(food)
        
        # Draw snake
        for i, pos in enumerate(self.snake):
            is_head = i == 0
            snake_part = ft.Container(
                width=CELL_SIZE,
                height=CELL_SIZE,
                left=pos[0] * (CELL_SIZE + CELL_SPACING),
                top=pos[1] * (CELL_SIZE + CELL_SPACING),
                bgcolor=SNAKE_COLORS["head"] if is_head else SNAKE_COLORS["body"],
                border_radius=CELL_BORDER_RADIUS,
                border=SNAKE_HEAD_BORDER if is_head else SNAKE_BODY_BORDER,
                animate=SNAKE_HEAD_ANIMATION if is_head else SNAKE_BODY_ANIMATION,
            )
            board_content.append(snake_part)
        
        # Update board
        self.board.content.controls = board_content
        self.page.update()

    def load_high_scores(self):
        """Load high scores from file"""
        try:
            if os.path.exists(self.high_scores_file):
                with open(self.high_scores_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading high scores: {e}")
            return []

    def save_high_scores(self):
        """Save high scores to file"""
        try:
            with open(self.high_scores_file, 'w') as f:
                json.dump(self.high_scores, f)
        except Exception as e:
            print(f"Error saving high scores: {e}")

    def load_settings(self):
        """Load saved settings"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    self.saved_speed_value = settings.get('speed', 50)
                    self.saved_volume_value = settings.get('volume', 50)
            else:
                self.saved_speed_value = 50
                self.saved_volume_value = 50
                self.save_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.saved_speed_value = 50
            self.saved_volume_value = 50

    def save_settings(self):
        """Save current settings"""
        try:
            settings = {
                'speed': self.speed_slider.value,
                'volume': self.volume_slider.value
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def update_high_scores(self):
        """Update the high scores list with the current score"""
        if self.score > 0:  # Only add scores greater than 0
            # Check if this exact score already exists
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
            new_score = {
                'score': self.score,
                'date': current_time
            }
            
            # Check if this score was just added (avoid duplicates)
            score_exists = any(
                score['score'] == self.score and 
                score['date'] == current_time 
                for score in self.high_scores
            )
            
            if not score_exists:
                # Add new score
                self.high_scores.append(new_score)
                
                # Sort scores in descending order
                self.high_scores.sort(key=lambda x: x['score'], reverse=True)
                
                # Keep only top 10 scores
                self.high_scores = self.high_scores[:10]
                
                # Save to file
                self.save_high_scores()
            
            # Update displayed high score
            self.high_score_text.value = f"High Score: {self.get_highest_score()}"
            self.page.update()

    def get_highest_score(self):
        if not self.high_scores:
            return 0
        return self.high_scores[0]['score']

    def toggle_scores_card(self):
        self.show_scores_card = not self.show_scores_card
        self.scores_card.visible = self.show_scores_card
        if self.show_scores_card:
            # Update scores when showing card
            self.scores_card.content.controls[2].controls[0].value = self.show_high_scores()
        self.page.update()

    def show_high_scores(self):
        if not self.high_scores:
            return "No high scores yet!"
        
        scores_text = ""
        for i, score in enumerate(self.high_scores, 1):
            date = score['date']
            points = score['score']
            if i == 1:
                scores_text += f"🥇{points} pts ({date})\n"
            elif i == 2:
                scores_text += f"🥈{points} pts ({date})\n"
            elif i == 3:
                scores_text += f"🥉{points} pts ({date})\n"
            else:
                scores_text += f"{i}. {points} pts ({date})\n"
        return scores_text

    async def loop_background_music(self):
        current_music = "normal"
        while True:
            if not self.paused and not self.game_over:
                if self.food_type == "special" and current_music != "special":
                    self.music.pause()
                    self.music2.resume()
                    current_music = "special"
                elif self.food_type == "normal" and current_music != "normal":
                    self.music2.pause()
                    self.music.resume()
                    current_music = "normal"
            await asyncio.sleep(0.1)

async def main(page: ft.Page):
    game = SnakeGame(page)
    await game.game_loop()

if __name__ == "__main__":
    ft.app(target=main)
