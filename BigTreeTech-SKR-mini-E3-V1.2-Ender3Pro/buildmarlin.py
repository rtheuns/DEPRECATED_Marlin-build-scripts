import re
import os
import shutil
import datetime
import io


MARLIN_DIR = 'Marlin'  
CONFIG_DIR = 'Configurations'
CONFIG_BASE = 'Creality/Ender-3 Pro/CrealityV1'

CONFIGURATION_H = f'{MARLIN_DIR}/Marlin/Configuration.h'
CONFIGURATION_ADV_H = f'{MARLIN_DIR}/Marlin/Configuration_adv.h'

MODIFICATION_TAG = 'RTMOD'

# BRANCH='bugfix-2.0.x'
BRANCH='2.0.x'
CONFIG_BRANCH='release-2.0.7.2'

def sed(pattern, replace, file, commentsymbol = '//'):
  print(f'   {replace}')

  source = io.open(file, 'r', encoding="utf-8")
  lines = source.readlines()

  dest = io.open(file, 'w', encoding="utf-8")  

  for line in lines:
    dest.write(re.sub(pattern, replace + f' {commentsymbol} [{MODIFICATION_TAG}]', line))



def load_codebase():
  if not os.path.exists(CONFIG_DIR):
    os.system(f'git clone https://github.com/MarlinFirmware/Configurations {CONFIG_DIR}')
    os.system(f'git -C {CONFIG_DIR} checkout {CONFIG_BRANCH}')
  else:
    print('Marlin configurations directory already exists.')

  if not os.path.exists(MARLIN_DIR):
    os.system(f'git clone https://github.com/MarlinFirmware/Marlin {MARLIN_DIR}')
    os.system(f'git -C {MARLIN_DIR} checkout {BRANCH}')

    shutil.copy(f'{CONFIG_DIR}/config/examples/{CONFIG_BASE}/Configuration.h', f'{MARLIN_DIR}/Marlin')
    shutil.copy(f'{CONFIG_DIR}/config/examples/{CONFIG_BASE}/Configuration_adv.h', f'{MARLIN_DIR}/Marlin')
    shutil.copy(f'{CONFIG_DIR}/config/examples/{CONFIG_BASE}/_Statusscreen.h', f'{MARLIN_DIR}/Marlin')
    shutil.copy(f'{CONFIG_DIR}/config/examples/{CONFIG_BASE}/_Bootscreen.h', f'{MARLIN_DIR}/Marlin')    
  else:
    print('Marlin codebase directory already exists.')



def build_codebase():
  os.system(f'platformio run -d {MARLIN_DIR}')


def main():
  load_codebase()

  set_info()
  set_machine()
  set_lcd_tweaks()
  set_skr_mini_e3()
  set_extra_safety()
  set_material_presets()
  set_pid_tuning()
  set_skew_correction()
  set_home_and_parking()
  set_bed_center()
  set_sdcard()
  set_bltouch()

  build_codebase()



#
# Info
#
def set_info():
  print('Configuring info')

  currentdate = datetime.datetime.today().strftime('%Y-%m-%d')

  sed(r'#define STRING_CONFIG_H_AUTHOR .*', '#define STRING_CONFIG_H_AUTHOR "Ender-3 Pro"', CONFIGURATION_H)
  #sed(r'.*#define CUSTOM_VERSION_FILE.*', '\n#define WEBSITE_URL "www.creality3d.cn"', CONFIGURATION_H)  
  sed(r'.*#define CUSTOM_VERSION_FILE.*', f'\n#define STRING_DISTRIBUTION_DATE "{currentdate}"', CONFIGURATION_H)
  sed(r'.*#define STRING_DISTRIBUTION_DATE.*', f'#define STRING_DISTRIBUTION_DATE "{currentdate}"', CONFIGURATION_H)
  sed(r'.*#define MACHINE_UUID .*', '#define MACHINE_UUID "0c0f870d-9d03-4bed-b217-9195f1f3941e"', CONFIGURATION_H)
  sed(r'#define CUSTOM_MACHINE_NAME .*', '#define CUSTOM_MACHINE_NAME "Ender-3 Pro"', CONFIGURATION_H) 
  sed(r'.*#define BOOTSCREEN_TIMEOUT .*', '  #define BOOTSCREEN_TIMEOUT 1000', CONFIGURATION_ADV_H)



#
# Machine
#
def set_machine():
  print('Configuring machine')

  sed(r'.*#define EXTRUDE_MAXLENGTH .*', '#define EXTRUDE_MAXLENGTH 500', CONFIGURATION_H)

  # axis
  sed(r'#define DEFAULT_AXIS_STEPS_PER_UNIT .*', '#define DEFAULT_AXIS_STEPS_PER_UNIT   { 80.2, 80.2, 400, 140 }', CONFIGURATION_H)

  # set extruder direction for trianglelabs mini extruder
  sed(r'#define INVERT_E0_DIR .*', '#define INVERT_E0_DIR false', CONFIGURATION_H)

  # modify junction deviation
  # sed(r'.*#define JUNCTION_DEVIATION_MM .*', '  #define JUNCTION_DEVIATION_MM 0.04  // (mm) Distance from real junction edge', CONFIGURATION_H)
  sed(r'.*#define JUNCTION_DEVIATION_MM .*', '  #define JUNCTION_DEVIATION_MM 0.08  // (mm) Distance from real junction edge', CONFIGURATION_H)

  # enable s-curve acceleration
  sed(r'.*#define S_CURVE_ACCELERATION.*', '#define S_CURVE_ACCELERATION', CONFIGURATION_H)
  # sed(r'.*#define S_CURVE_ACCELERATION.*', '//#define S_CURVE_ACCELERATION', CONFIGURATION_H)

  # disable arc support
  sed(r'.*#define ARC_SUPPORT .*', '//#define ARC_SUPPORT                 // Disable this feature to save ~3226 bytes', CONFIGURATION_ADV_H)

  # linear advance
  sed(r'^#define LIN_ADVANCE.*', '//#define LIN_ADVANCE', CONFIGURATION_ADV_H)
  # sed(r'//#define LIN_ADVANCE.*', '#define LIN_ADVANCE', CONFIGURATION_ADV_H)
  # sed(r' *#define LIN_ADVANCE_K .*', '  #define LIN_ADVANCE_K 0.0     // Unit: mm compression per 1mm/s extruder speed', CONFIGURATION_ADV_H)
  # sed(r'#define DEFAULT_EJERK .*', '#define DEFAULT_EJERK    15  // May be used by Linear Advance', CONFIGURATION_H)
  # sed(r'//#define EXPERIMENTAL_SCURVE.*', '#define EXPERIMENTAL_SCURVE   // Enable this option to permit S-Curve Acceleration', CONFIGURATION_ADV_H)



#
# Home and parking configuration
# 
def set_home_and_parking():
  sed(r'.*#define INDIVIDUAL_AXIS_HOMING_MENU .*', '//#define INDIVIDUAL_AXIS_HOMING_MENU', CONFIGURATION_H)
  sed(r'.*#define Z_HOMING_HEIGHT .*', '#define Z_HOMING_HEIGHT 10        // (mm) Minimal Z height before homing (G28) for Z clearance above the bed, clamps, ...', CONFIGURATION_H)
  sed(r'.*#define Z_AFTER_HOMING .*', '#define Z_AFTER_HOMING  10        // (mm) Height to move to after homing Z', CONFIGURATION_H)
  sed(r'.*#define HOMING_FEEDRATE_XY .*', '#define HOMING_FEEDRATE_XY (60*60)', CONFIGURATION_H)
  sed(r'.*#define HOMING_FEEDRATE_Z .*', '#define HOMING_FEEDRATE_Z  (20*60)', CONFIGURATION_H)
  sed(r'.*#define ENDSTOPS_ALWAYS_ON_DEFAULT.*', '#define ENDSTOPS_ALWAYS_ON_DEFAULT', CONFIGURATION_ADV_H)

  # nozzle parking
  sed(r'.*#define NOZZLE_PARK_FEATURE.*', '#define NOZZLE_PARK_FEATURE', CONFIGURATION_H)
  sed(r'.*#define NOZZLE_PARK_POINT .*', '  #define NOZZLE_PARK_POINT { 25, 200, 100 }', CONFIGURATION_H)  # { 25, 175, 100 }
  sed(r'.*#define NOZZLE_PARK_Z_FEEDRATE .*', '  #define NOZZLE_PARK_Z_FEEDRATE   15   // (mm/s) Z axis feedrate (not used for delta printers)', CONFIGURATION_H)
  sed(r'.*#define EVENT_GCODE_SD_STOP .*', '  #define EVENT_GCODE_SD_STOP "G27 P2"       // G-code to run on Stop Print (e.g., "G28XY" or "G27")', CONFIGURATION_ADV_H)

  # pause (filament load and unload)
  sed(r'.*#define ADVANCED_PAUSE_FEATURE.*', '#define ADVANCED_PAUSE_FEATURE', CONFIGURATION_ADV_H)
  sed(r'.*#define FILAMENT_CHANGE_UNLOAD_LENGTH .*', '  #define FILAMENT_CHANGE_UNLOAD_LENGTH      450  // (mm) The length of filament for a complete unload.', CONFIGURATION_ADV_H)
  sed(r'.*#define FILAMENT_CHANGE_FAST_LOAD_LENGTH .*', '  #define FILAMENT_CHANGE_FAST_LOAD_LENGTH   420  // (mm) Load length of filament, from extruder gear to nozzle.', CONFIGURATION_ADV_H)


#
# Bed center fix
#
def set_bed_center():
  #sed(r'#define X_MAX_POS .*', '#define X_MAX_POS 243 // for BLTouch', CONFIGURATION_H)
  #sed(r'#define Y_MIN_POS .*', '#define Y_MIN_POS -6', CONFIGURATION_H)
  #sed(r'#define X_BED_SIZE .*', '#define X_BED_SIZE 231', CONFIGURATION_H)
  #sed(r'#define Y_BED_SIZE .*', '#define Y_BED_SIZE 231', CONFIGURATION_H)

  sed(r'#define X_MAX_POS .*', '#define X_MAX_POS X_BED_SIZE', CONFIGURATION_H)
  sed(r'#define Y_MIN_POS .*', '#define Y_MIN_POS 0', CONFIGURATION_H)
  sed(r'#define X_BED_SIZE .*', '#define X_BED_SIZE 235', CONFIGURATION_H)
  sed(r'#define Y_BED_SIZE .*', '#define Y_BED_SIZE 235', CONFIGURATION_H)



#
# LCD tweaks
#
def set_lcd_tweaks():
  # show percentage next to the progress bar
  sed(r'.*#define DOGM_SD_PERCENT.*', '  #define DOGM_SD_PERCENT', CONFIGURATION_ADV_H)
  sed(r'.*#define DOGM_SPI_DELAY_US.*', '    #define DOGM_SPI_DELAY_US 5', CONFIGURATION_ADV_H)

  # add an 'M73' G-code to set the current percentage
  sed(r'.*#define LCD_SET_PROGRESS_MANUALLY.*', '#define LCD_SET_PROGRESS_MANUALLY', CONFIGURATION_ADV_H)

  sed(r'.*#define SHOW_REMAINING_TIME .*', '  #define SHOW_REMAINING_TIME          // Display estimated time to completion', CONFIGURATION_ADV_H)
  sed(r'.*#define USE_M73_REMAINING_TIME .*', '    #define USE_M73_REMAINING_TIME     // Use remaining time from M73 command instead of estimation', CONFIGURATION_ADV_H)
  sed(r'.*#define ROTATE_PROGRESS_DISPLAY .*', '    #define ROTATE_PROGRESS_DISPLAY    // Display (P)rogress, (E)lapsed, and (R)emaining time', CONFIGURATION_ADV_H)

  sed(r'.*#define BABYSTEP_MULTIPLICATOR_Z .*', '  #define BABYSTEP_MULTIPLICATOR_Z  5       // (steps or mm) Steps or millimeter distance for each Z babystep', CONFIGURATION_ADV_H)
  sed(r'.*#define BABYSTEP_MULTIPLICATOR_XY .*', '  #define BABYSTEP_MULTIPLICATOR_XY 5       // (steps or mm) Steps or millimeter distance for each XY babystep',  CONFIGURATION_ADV_H)
  sed(r'.*#define BABYSTEP_DISPLAY_TOTAL .*', '  #define BABYSTEP_DISPLAY_TOTAL            // Display total babysteps since last G28', CONFIGURATION_ADV_H)
  sed(r'.*#define BABYSTEP_ZPROBE_OFFSET .*', '  #define BABYSTEP_ZPROBE_OFFSET            // Combine M851 Z and Babystepping', CONFIGURATION_ADV_H)
  sed(r'.*#define BABYSTEP_ZPROBE_GFX_OVERLAY .*', '    #define BABYSTEP_ZPROBE_GFX_OVERLAY     // Enable graphical overlay on Z-offset editor', CONFIGURATION_ADV_H)



#
# SD Card
#
def set_sdcard():
  sed(r'.*#define SDCARD_SORT_ALPHA.*', '#define SDCARD_SORT_ALPHA', CONFIGURATION_ADV_H)



#
# SKR Mini E3 v1.2 board specific configuration
#
def set_skr_mini_e3():
  print('Configuring SKR Mini E3 v1.2 mainboard')

  # sed(r'default_envs.*=.*', 'default_envs = STM32F103RC_btt_512K', f'{MARLIN_DIR}/platformio.ini', '#')
  sed(r'default_envs.*=.*', 'default_envs = STM32F103RC_btt', f'{MARLIN_DIR}/platformio.ini', '#')

  sed(r'#define SERIAL_PORT .*', '#define SERIAL_PORT 2', CONFIGURATION_H)
  sed(r'/*#define SERIAL_PORT_2 .*', '#define SERIAL_PORT_2 -1', CONFIGURATION_H)
  sed(r'#define BAUDRATE .*', '#define BAUDRATE 250000', CONFIGURATION_H) # 115200

  sed(r' *#define MOTHERBOARD .*', '  #define MOTHERBOARD BOARD_BTT_SKR_MINI_E3_V1_2', CONFIGURATION_H)

  sed(r'/*#define X_DRIVER_TYPE .*', '#define X_DRIVER_TYPE  TMC2209', CONFIGURATION_H)
  sed(r'/*#define Y_DRIVER_TYPE .*', '#define Y_DRIVER_TYPE  TMC2209', CONFIGURATION_H)
  sed(r'/*#define Z_DRIVER_TYPE .*', '#define Z_DRIVER_TYPE  TMC2209', CONFIGURATION_H)
  sed(r'/*#define E0_DRIVER_TYPE .*', '#define E0_DRIVER_TYPE TMC2209', CONFIGURATION_H)

  # tmc stepper driver hybrid stealthchop/spreadcycle
  #sed(r'.*#define MONITOR_DRIVER_STATUS', '  #define MONITOR_DRIVER_STATUS', CONFIGURATION_ADV_H)

  sed(r'.*#define ADAPTIVE_STEP_SMOOTHING.*', '#define ADAPTIVE_STEP_SMOOTHING', CONFIGURATION_ADV_H)

  #sed(r'.*#define HYBRID_THRESHOLD', '  #define HYBRID_THRESHOLD', CONFIGURATION_ADV_H)
  #sed(r'.*#define X_HYBRID_THRESHOLD .*', '  #define X_HYBRID_THRESHOLD     170@g', CONFIGURATION_ADV_H)
  #sed(r'.*#define Y_HYBRID_THRESHOLD .*', '  #define Y_HYBRID_THRESHOLD     170@g', CONFIGURATION_ADV_H)
  #sed(r'.*#define Z_HYBRID_THRESHOLD .*', '  #define Z_HYBRID_THRESHOLD      20@g', CONFIGURATION_ADV_H)
  #sed(r'.*#define E0_HYBRID_THRESHOLD .*', '  #define E0_HYBRID_THRESHOLD     20@g', CONFIGURATION_ADV_H)

  sed(r'.*#define SQUARE_WAVE_STEPPING.*', '  #define SQUARE_WAVE_STEPPING', CONFIGURATION_ADV_H)
 
  sed(r'.*#define SPEAKER.*', '//#define SPEAKER', CONFIGURATION_H)
  sed(r'.*#define CR10_STOCKDISPLAY.*', '#define CR10_STOCKDISPLAY', CONFIGURATION_H)
  sed(r'.*#define FAN_SOFT_PWM.*', '#define FAN_SOFT_PWM', CONFIGURATION_H)



#
# Set extra safety measurements
#
def set_extra_safety():
  print('Configuring extra safety measurements')

  # limit z height
  sed(r'#define Z_MAX_POS .*', '#define Z_MAX_POS 220', CONFIGURATION_H)

  # make sure bed pid temp remains disabled, to keep compatibility with flex-steel pei
  sed(r'.*#define PIDTEMPBED.*', '//#define PIDTEMPBED', CONFIGURATION_H)

  # add a little more safety, limits selectable temp to 10 degrees less
  sed(r'#define BED_MAXTEMP .*', '#define BED_MAXTEMP      90', CONFIGURATION_H)

  # add a little more safety against too cold filament
  sed(r'#define EXTRUDE_MINTEMP .*', '#define EXTRUDE_MINTEMP 175', CONFIGURATION_H)

  # add a little more safety, limits selectable temp to 15 degrees less
  sed(r'#define HEATER_0_MAXTEMP 275', '#define HEATER_0_MAXTEMP 265', CONFIGURATION_H)

  # prevent filament cooking
  sed(r'^//#define HOTEND_IDLE_TIMEOUT.*', '#define HOTEND_IDLE_TIMEOUT', CONFIGURATION_ADV_H)
  sed(r'.*#define HOTEND_IDLE_MIN_TRIGGER .*', '  #define HOTEND_IDLE_MIN_TRIGGER   170     // (°C) Minimum temperature to enable hotend protection', CONFIGURATION_ADV_H) 



#
# Material presets
#
def set_material_presets():
  print('Configuring material presets')

  # modernize pla preset
  sed(r'#define PREHEAT_1_TEMP_HOTEND .*', '#define PREHEAT_1_TEMP_HOTEND 200', CONFIGURATION_H)
  sed(r'#define PREHEAT_1_TEMP_BED .*', '#define PREHEAT_1_TEMP_BED     60', CONFIGURATION_H)
 
  # change abs preset to petg
  sed(r'#define PREHEAT_2_LABEL .*', '#define PREHEAT_2_LABEL       "PETG"', CONFIGURATION_H)
  sed(r'#define PREHEAT_2_TEMP_HOTEND .*', '#define PREHEAT_2_TEMP_HOTEND 240', CONFIGURATION_H)
  sed(r'#define PREHEAT_2_TEMP_BED .*', '#define PREHEAT_2_TEMP_BED     70', CONFIGURATION_H)



#
# Pid tuning
#
def set_pid_tuning():
  print('Configuring pid tuning')

  sed(r'  #define DEFAULT_Kp .*', '  #define DEFAULT_Kp 21.73', CONFIGURATION_H)
  sed(r'  #define DEFAULT_Ki .*', '  #define DEFAULT_Ki 1.54', CONFIGURATION_H)
  sed(r'  #define DEFAULT_Kd .*', '  #define DEFAULT_Kd 76.55', CONFIGURATION_H)



#
# Skew correction
#
def set_skew_correction():
  print('Configuring skew correction')

  sed(r'^//#define SKEW_CORRECTION.*', '#define SKEW_CORRECTION', CONFIGURATION_H)
  sed(r' *#define XY_DIAG_AC .*', '  #define XY_DIAG_AC 141.44', CONFIGURATION_H)
  sed(r' *#define XY_DIAG_BD .*', '  #define XY_DIAG_BD 141.66', CONFIGURATION_H)
  sed(r' *#define XY_SIDE_AD .*', '  #define XY_SIDE_AD 100', CONFIGURATION_H)



#
# BLTouch
#
def set_bltouch():
  # bltouch probe as z-endstop on z-endstop connector
  sed(r'^/*#define Z_SAFE_HOMING.*', '#define Z_SAFE_HOMING', CONFIGURATION_H)
  sed(r'.*#define Z_MIN_PROBE_USES_Z_MIN_ENDSTOP_PIN.*', '#define Z_MIN_PROBE_USES_Z_MIN_ENDSTOP_PIN', CONFIGURATION_H)

  # use probe connector as z-endstop connector
  sed(r'.*#define Z_STOP_PIN.*', '#define Z_STOP_PIN                          PC14  // "Z-STOP" (BLTouch)', f'{MARLIN_DIR}/Marlin/src/pins/stm32f1/pins_BTT_SKR_MINI_E3_common.h')

  sed(r'/*#define BLTOUCH.*', '#define BLTOUCH', CONFIGURATION_H)
  sed(r'/*#define LCD_BED_LEVELING.*', '#define LCD_BED_LEVELING', CONFIGURATION_H)  
  sed(r'.*#define GRID_MAX_POINTS_X .*', '  #define GRID_MAX_POINTS_X 3', CONFIGURATION_H)
  sed(r'^/*#define NOZZLE_TO_PROBE_OFFSET .*', '#define NOZZLE_TO_PROBE_OFFSET { -44, -6, 0 }', CONFIGURATION_H)  # { -43, -5, 0 }
  sed(r'/*#define EXTRAPOLATE_BEYOND_GRID.*', '#define EXTRAPOLATE_BEYOND_GRID', CONFIGURATION_H)
  sed(r'.*#define PROBING_MARGIN .*', '#define PROBING_MARGIN 44', CONFIGURATION_H) # 44 or 31
  sed(r'.*#define XY_PROBE_SPEED .*', '#define XY_PROBE_SPEED 10000', CONFIGURATION_H)
  sed(r'.*#define Z_CLEARANCE_DEPLOY_PROBE .*', '#define Z_CLEARANCE_DEPLOY_PROBE   10 // Z Clearance for Deploy/Stow', CONFIGURATION_H)
  sed(r'.*#define Z_AFTER_PROBING .*', '#define Z_AFTER_PROBING            10 // Z position after probing is done', CONFIGURATION_H)
  sed(r'.*#define BLTOUCH_LCD_VOLTAGE_MENU.*', '  #define BLTOUCH_LCD_VOLTAGE_MENU', CONFIGURATION_ADV_H)

  # bed leveling
  sed(r'/*#define AUTO_BED_LEVELING_BILINEAR.*', '#define AUTO_BED_LEVELING_BILINEAR', CONFIGURATION_H)
  sed(r'.*#define MESH_BED_LEVELING.*', '//#define MESH_BED_LEVELING', CONFIGURATION_H)



#
# Main function
#
if __name__ == "__main__":
  main()
