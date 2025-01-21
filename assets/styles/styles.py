from flet import (
    Colors,
    LinearGradient,
    alignment,
    padding,
    animation,
    AnimationCurve,
    border,
    BoxShadow,
    Offset,
)

# Color scheme
BACKGROUND_COLOR = Colors.GREY_50
BOARD_COLOR = Colors.GREY_100
GRID_COLOR = Colors.GREY_200
BORDER_COLOR = Colors.BLUE_GREY_200
SNAKE_COLORS = {
    "head": Colors.LIGHT_GREEN_ACCENT_400,
    "body": Colors.LIGHT_GREEN_400,
    "head_outline": Colors.LIGHT_GREEN_700,
    "body_outline": Colors.LIGHT_GREEN_600,
}
FOOD_COLOR = Colors.PINK_400
FOOD_OUTLINE_COLOR = Colors.PINK_600
SPECIAL_FOOD_COLOR = Colors.BLUE_400
SPECIAL_FOOD_OUTLINE_COLOR = Colors.BLUE_600
TEXT_COLOR = Colors.BLUE_GREY_900
SCORE_COLOR = Colors.BLUE_600
GAME_OVER_COLOR = Colors.RED_500
CONTROLS_COLOR = Colors.BLUE_GREY_600
KEY_COLOR = Colors.BLUE_GREY_800

# Dimensions
GRID_SIZE = 20  # Number of cells in each direction
BOARD_SIZE = 500  # Fixed board size in pixels
BOARD_PADDING = 10  # Padding inside the board
CELL_SPACING = 2  # Space between cells

# Calculate cell size to fit perfectly in the board
PLAYABLE_SIZE = BOARD_SIZE - (2 * BOARD_PADDING)  # Size minus padding
TOTAL_SPACING = CELL_SPACING * (GRID_SIZE - 1)  # Total space used by spacing
CELL_SIZE = (PLAYABLE_SIZE - TOTAL_SPACING) // GRID_SIZE  # Cell size that fits perfectly

# Game settings
DEFAULT_SPEED = 0.08  # Default speed
MAX_SPEED = 0.02  # Fastest speed (lower number = faster)
MIN_SPEED = 0.2  # Slowest speed
SPEED_INCREASE = 0.995  # Speed increase factor

# Animation settings
MOVE_DURATION = 150  # Movement animation duration in milliseconds
FOOD_ANIMATION = animation.Animation(400, AnimationCurve.BOUNCE_OUT)
SNAKE_HEAD_ANIMATION = animation.Animation(MOVE_DURATION, AnimationCurve.EASE_OUT)
SNAKE_BODY_ANIMATION = animation.Animation(MOVE_DURATION, AnimationCurve.EASE_IN_OUT)
SCORE_ANIMATION = animation.Animation(150, AnimationCurve.BOUNCE_OUT)

# Styles
BOARD_BORDER_RADIUS = 10
CELL_BORDER_RADIUS = 6
SHADOW = 5

# Border styles
SNAKE_HEAD_BORDER = border.all(2, SNAKE_COLORS["head_outline"])
SNAKE_BODY_BORDER = border.all(2, SNAKE_COLORS["body_outline"])
FOOD_BORDER = border.all(2, FOOD_OUTLINE_COLOR)

# Text styles
TITLE_STYLE = {
    "size": 32,
    "color": TEXT_COLOR,
    "weight": "bold",
}

SCORE_STYLE = {
    "size": 24,
    "color": SCORE_COLOR,
    "weight": "w600",
}

GAME_OVER_STYLE = {
    "size": 28,
    "color": GAME_OVER_COLOR,
    "weight": "bold",
}

INSTRUCTION_STYLE = {
    "size": 16,
    "color": TEXT_COLOR,
    "weight": "w500",
}

CONTROLS_STYLE = {
    "size": 14,
    "color": CONTROLS_COLOR,
    "weight": "w400",
}

# Separate text and container styles for key display
KEY_TEXT_STYLE = {
    "size": 14,
    "color": KEY_COLOR,
    "weight": "w600",
}

KEY_CONTAINER_STYLE = {
    "bgcolor": Colors.BLUE_GREY_50,
    "padding": 4,
    "border_radius": 4,
}

# Card styles
CARD_STYLE = {
    "bgcolor": Colors.WHITE,
    "border_radius": 15,
    "padding": 20,
    "shadow": BoxShadow(
        spread_radius=1,
        blur_radius=15,
        color=Colors.with_opacity(0.15, Colors.BLACK),
        offset=Offset(0, 5),
    ),
}

CARD_TITLE_STYLE = {
    "size": 24,
    "color": TEXT_COLOR,
    "weight": "bold",
}

CLOSE_BUTTON_STYLE = {
    "icon_color": Colors.GREY_400,
    "icon_size": 20,
}

SCORES_LIST_STYLE = {
    "size": 16,
    "color": TEXT_COLOR,
    "weight": "w500",
}

SCORE_ITEM_STYLE = {
    "size": 14,
    "color": CONTROLS_COLOR,
    "weight": "w400",
}
