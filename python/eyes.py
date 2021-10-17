import pygame
from pygame.locals import *
from pygame.compat import geterror
import math
import random
from threading import Lock, Thread
from orange_utils import OrangeOpType

WIDTH = 1024
HEIGHT = 600
_PUPIL_MOVE_RATE = 20

_going = False
_angle = 0
_offset = 0
_targetAngle = 0
_targetOffset = 0
_dims = None
_eyeAngleOffsetLock = Lock()
_text_card_text = ""

CMD_TEXT_BOX_LABEL = "Cmd:"
UI_TITLE_TEXT = "Orange Control"
BATT_TEXT_BOX_LABEL = "Battery:"
IP_ADDR_TEXT_BOX_LABEL = "IP Addr:"
LAST_SPEECH_HEARD_LABEL = "Last heard:"
LAST_SPEECH_SPOKEN_LABEL = "Last spoken:"
EXIT_BUTTON_LABEL = "Exit"
GOOGLE_MODE_BUTTON_LABEL = "Google Speech"

def update():
    pass

def draw_eyes(screen, pupil_angle=0, pupil_offset=0):
#    screen.fill((0, 0, 0))
    pupil_angle = math.radians(pupil_angle)
    def draw_eye(eye_x, eye_y, pupil_angle, pupil_offset):
        #mouse_x, mouse_y = pygame.mouse.get_pos()

        #distance_x = mouse_x - eye_x
        #distance_y = mouse_y - eye_y
        #distance = min(math.sqrt(distance_x**2 + distance_y**2), 70)
        pupil_offset = min(pupil_offset, 70)
        #angle = math.atan2(distance_y, distance_x)

        pupil_x = int(eye_x + (math.cos(pupil_angle) * pupil_offset))
        pupil_y = int(eye_y + (math.sin(pupil_angle) * pupil_offset))

        pygame.draw.circle(screen, (255, 255, 255), (eye_x, eye_y), 150)
        pygame.draw.circle(screen, (0, 0, 100), (pupil_x, pupil_y), 50)

    draw_eye(_dims[0] / 3 - 40, _dims[1]/ 2, pupil_angle, pupil_offset)
    draw_eye(2*_dims[0] / 3 + 40, _dims[1]/ 2, pupil_angle, pupil_offset)

def shutdown():
    global _going
    _going = False

def set(angle=None, offset=None):
    global _angle, _offset, _targetAngle, _targetOffset
    with _eyeAngleOffsetLock:
        if angle is not None:
            _angle = angle
            _targetAngle = angle
        if offset is not None:
            _offset = offset
            _targetOffset = offset

def next_blink_time():
    return pygame.time.get_ticks() + 1000 + (random.random()*6000)

def setHome():
    global _targetAngle, _targetOffset
    with _eyeAngleOffsetLock:
        _targetAngle = 0
        _targetOffset = 0

def setAngleOffset(targetAngle=None, targetOffset=None):
    global _targetAngle, _targetOffset
    with _eyeAngleOffsetLock:
        if targetAngle is not None:
            _targetAngle = targetAngle
        if targetOffset is not None:
            _targetOffset = targetOffset

def setText(text, time=5):
    global _text_card_text, _text_card_text_end_time
    _text_card_text = text
    _text_card_text_end_time = pygame.time.get_ticks() + time * 1000

def start(handle_op_request, ):
    global _going, _dims, _angle, _offset, _text, _text_card_text_end_time
    _going = True

    google_mode = handle_op_request(OrangeOpType.GoogleSpeech)

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    _dims = screen.get_size()
#    pygame.display.set_caption('Orange Eyes')

       # Create The Backgound
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))

      # Put Text On The Background, Centered
    # if pygame.font:
    #     font = pygame.font.Font(None, 36)
    #     text = font.render("Orange Eyes", 1, (10, 10, 10))
    #     textpos = text.get_rect(centerx=background.get_width()/2)
    #     background.blit(text, textpos)

    # basic font for user typed
    base_font = pygame.font.Font(None, 32)
    button_font = pygame.font.Font(None, 48)
    title_font = pygame.font.Font(None, 60)

    # title text
    title_text_surface = title_font.render(UI_TITLE_TEXT, True, "orange")
    title_text_pos = title_text_surface.get_rect(centerx=background.get_width()/2, centery=33)

    cmd_text = ''
    
    # create battery % field
    batt_box_rect = pygame.Rect(350, 100, 50, 32)
    batt_box_label_surface = base_font.render(BATT_TEXT_BOX_LABEL, True, "orange")

    # create IP address field
    ip_addr_box_rect = pygame.Rect(350, 150, 100, 32)
    ip_addr_box_label_surface = base_font.render(IP_ADDR_TEXT_BOX_LABEL, True, "orange")

    # create last heard
    last_heard_box_rect = pygame.Rect(350, 200, 200, 32)
    last_heard_box_label_surface = base_font.render(LAST_SPEECH_HEARD_LABEL, True, "orange")

    # create last spoken
    last_spoken_box_rect = pygame.Rect(350, 250, 200, 32)
    last_spoken_box_label_surface = base_font.render(LAST_SPEECH_SPOKEN_LABEL, True, "orange")

    # create google mode button
    google_mode_button_rect = pygame.Rect(20, 380, 180, 50)
    google_mode_button_label_surface = base_font.render(GOOGLE_MODE_BUTTON_LABEL, True, "orange")

    # create exit box button
    exit_box_rect = pygame.Rect(20, 20, 150, 100)
    exit_box_label_surface = button_font.render(EXIT_BUTTON_LABEL, True, "orange")
    
    # create cmd box rectangle
    cmd_box_rect = pygame.Rect(350, 300, 300, 32)
    
    # color_active stores color(lightskyblue3) which
    # gets active when input box is clicked by user
    color_active = pygame.Color('lightskyblue3')
    
    # color_passive store color(chartreuse4) which is
    # color of input box.
    color_passive = pygame.Color('chartreuse4')
    cmd_box_color = color_passive

    button_off_color = pygame.Color('black')
    button_on_color = pygame.Color('chartreuse4')

    google_mode_color = button_on_color if google_mode else button_off_color

    cmd_box_active = False
    cmd_box_label_surface = base_font.render(CMD_TEXT_BOX_LABEL, True, "orange")
    
    # Display The Background
    screen.blit(background, (0, 0))
    pygame.display.flip()

     # Prepare Game Objects
    clock = pygame.time.Clock()
    time = pygame.time
    time_to_blink = next_blink_time()

    _text_card_text = ""
    if pygame.font:
        text_card_font = pygame.font.Font(None, 255)

                
    draw_eyes_enabled = True
    draw_ui_enabled = False

    # Main Loop
    try:
        while _going:
            clock.tick(30)

            # Handle Input Events
            for event in pygame.event.get():
                if event.type == QUIT:
                    going = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        draw_eyes_enabled = True
                        draw_ui_enabled = False
                    elif event.key == pygame.K_BACKSPACE:
                        # get text input from 0 to -1 i.e. end.
                        if cmd_box_active:
                            cmd_text = cmd_text[:-1]
                    # Unicode standard is used for string
                    # formation
                    else:
                        if cmd_box_active:
                            if event.key == pygame.K_RETURN:
                                handle_op_request(OrangeOpType.TextCommand, cmd_text)
                                cmd_text = ""
                            else:
                                cmd_text += event.unicode
                elif event.type == MOUSEBUTTONDOWN:
                    if draw_eyes_enabled:
                        draw_eyes_enabled = False
                        draw_ui_enabled = True
                    elif draw_ui_enabled:
                        if cmd_box_rect.collidepoint(event.pos):
                            cmd_box_active = True
                        else:
                            cmd_box_active = False                        
                        if exit_box_rect.collidepoint(event.pos):
                            draw_ui_enabled = False
                            draw_eyes_enabled = True
                        if google_mode_button_rect.collidepoint(event.pos):
                            google_mode = handle_op_request(OrangeOpType.ToggleGoogleSpeech)
                            google_mode_color = button_on_color if google_mode else button_off_color

            #allsprites.update()

            # Draw Everything
            screen.blit(background, (0, 0))
            #allsprites.draw(screen)
            with _eyeAngleOffsetLock:
                targetAngle = _targetAngle
                targetOffset = _targetOffset

            angleDiff = _targetAngle - _angle
            offsetDiff = _targetOffset - _offset
            if _offset != 0 and abs(angleDiff) >= _PUPIL_MOVE_RATE:
                _angle += math.copysign(_PUPIL_MOVE_RATE, angleDiff)
            else:
                _angle = _targetAngle
            if abs(offsetDiff) >= _PUPIL_MOVE_RATE:
                _offset += math.copysign(_PUPIL_MOVE_RATE, offsetDiff)
            else:
                _offset = _targetOffset

            if len(_text_card_text) > 0:
                if text_card_font:
                    text = text_card_font.render(_text_card_text, 1, (255, 255, 255))
                    textpos = text.get_rect(centerx=background.get_width()/2, centery=background.get_height()/2)
                    screen.blit(text, textpos)
                    if pygame.time.get_ticks() > _text_card_text_end_time:
                        _text_card_text = ""
            elif draw_eyes_enabled:
                draw_eyes(screen, _angle, _offset)
                #blink
                if time.get_ticks() > time_to_blink:
                    pygame.draw.rect(screen, (0,0,0), (0, 0, _dims[0], _dims[1]/2))
                    pygame.display.flip()
                    time.wait(40)
                    pygame.draw.rect(screen, (0,0,0), (0, _dims[1]/2, _dims[0], _dims[1] / 2))
                    pygame.display.flip()
                    time.wait(300)
                    time_to_blink = next_blink_time()
            elif draw_ui_enabled:
                if cmd_box_active:
                    cmd_box_color = color_active
                else:
                    cmd_box_color = color_passive

                # draw title 
                screen.blit(title_text_surface, title_text_pos)

                # draw exit button
                pygame.draw.rect(screen, color_passive, exit_box_rect, 8, 12)
                exit_text_pos = exit_box_label_surface.get_rect(centerx=(exit_box_rect.x + exit_box_rect.width/2), 
                                                                centery=(exit_box_rect.y + exit_box_rect.height/2))
                screen.blit(exit_box_label_surface, exit_text_pos)
                
                # draw google mode button
                pygame.draw.rect(screen, google_mode_color, google_mode_button_rect)
                google_mode_label_pos = google_mode_button_label_surface.get_rect(centerx=(google_mode_button_rect.x + google_mode_button_rect.width/2),
                                                          centery=(google_mode_button_rect.y + google_mode_button_rect.height/2))
                screen.blit(google_mode_button_label_surface, google_mode_label_pos)
                
                # draw batt %
                batt_text_surface = base_font.render(str(handle_op_request(OrangeOpType.BatteryPercent))+ "%", True, "lightgrey")
                screen.blit(batt_text_surface, (batt_box_rect.x+10, batt_box_rect.y+5))
                # draw label
                screen.blit(batt_box_label_surface, (batt_box_rect.x - batt_box_label_surface.get_width() - 5, batt_box_rect.y + 5))

                # draw last speech heard
                last_heard_text_surface = base_font.render(handle_op_request(OrangeOpType.LastSpeechHeard), True, "lightgray")
                screen.blit(last_heard_text_surface, (last_heard_box_rect.x+10, last_heard_box_rect.y+5))
                # draw label
                screen.blit(last_heard_box_label_surface, (last_heard_box_rect.x - last_heard_box_label_surface.get_width() - 5, last_heard_box_rect.y + 5))

                # draw last speech spoken
                last_spoken_text_surface = base_font.render(handle_op_request(OrangeOpType.LastSpeechSpoken), True, "lightgray")
                screen.blit(last_spoken_text_surface, (last_spoken_box_rect.x+10, last_spoken_box_rect.y+5))
                # draw label
                screen.blit(last_spoken_box_label_surface, (last_spoken_box_rect.x - last_spoken_box_label_surface.get_width() - 5, last_spoken_box_rect.y + 5))

                # draw last speech spoken
                ip_addr_text_surface = base_font.render(handle_op_request(OrangeOpType.IpAddress), True, "lightgray")
                screen.blit(ip_addr_text_surface, (ip_addr_box_rect.x+10, ip_addr_box_rect.y+5))
                # draw label
                screen.blit(ip_addr_box_label_surface, (ip_addr_box_rect.x - ip_addr_box_label_surface.get_width() - 5, ip_addr_box_rect.y + 5))

                # draw cmd entry label
                screen.blit(cmd_box_label_surface, (cmd_box_rect.x - cmd_box_label_surface.get_width() - 5, cmd_box_rect.y + 5))
                # draw rectangle and argument passed which should
                # be on screen
                pygame.draw.rect(screen, cmd_box_color, cmd_box_rect)            
                text_surface = base_font.render(cmd_text, True, (255, 255, 255))
                # render cmd text at position stated in arguments
                screen.blit(text_surface, (cmd_box_rect.x+5, cmd_box_rect.y+5))
                # set width of textfield so that text cannot get
                # outside of user's text input
                cmd_box_rect.w = max(100, text_surface.get_width()+10)                

            pygame.display.flip()
    except KeyboardInterrupt:
        None

    pygame.quit()
