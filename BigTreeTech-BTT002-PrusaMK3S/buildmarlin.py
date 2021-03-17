import re
import os
import shutil
import datetime
import io


MARLIN_DIR = 'Marlin'
CONFIG_DIR = 'Configurations'
EXTRACONFIG_DIR = 'Extraconfig'

CONFIG_BASE = 'Prusa/MK3S-BigTreeTech-BTT002'

PLATFORMIO_INI = f'{MARLIN_DIR}/platformio.ini'
CONFIGURATION_H = f'{MARLIN_DIR}/Marlin/Configuration.h'
CONFIGURATION_ADV_H = f'{MARLIN_DIR}/Marlin/Configuration_adv.h'
PINS = f'{MARLIN_DIR}/Marlin/src/pins/stm32f4/pins_BTT_BTT002_V1_0.h'

MODIFICATION_TAG = 'MYMOD'

MARLIN_REPO = 'https://github.com/rtheuns/Marlin'
MARLIN_BRANCH = 'marlin-sheets-feature'

CONFIG_REPO = 'https://github.com/Marlinfirmware/Configurations';
CONFIG_BRANCH = 'import-2.0.x'



#
# Helper function for setting tags in the configuration
#
def sed(pattern, replace, file, commentsymbol = '//'):
    print(f'   {replace}')

    source = io.open(file, 'r', encoding="utf-8")
    lines = source.readlines()

    dest = io.open(file, 'w', encoding="utf-8")

    for line in lines:
        dest.write(re.sub(pattern, replace + f' {commentsymbol} [{MODIFICATION_TAG}]', line))



#
# Helper method for merging a configfile with an additional config file
#
def merge_config(configfile_1, configfile_2, configfile_dest):
    with open(configfile_1) as fp: 
        data = fp.read() 
  
    with open(configfile_2) as fp: 
        data2 = fp.read() 
  
    data += "\n\n"
    data += data2 
  
    with open (configfile_dest, 'w') as fp: 
        fp.write(data) 



#
# Load Marlin codebase with configurations
#
def load_codebase():
    if not os.path.exists(CONFIG_DIR):
        os.system(f'git clone {CONFIG_REPO} {CONFIG_DIR}')
        os.system(f'git -C {CONFIG_DIR} checkout {CONFIG_BRANCH}')
    else:
        print('Marlin configuration directory already exists.')

    if not os.path.exists(MARLIN_DIR):
        os.system(f'git clone {MARLIN_REPO} {MARLIN_DIR}')
        os.system(f'git -C {MARLIN_DIR} checkout {MARLIN_BRANCH}')
    else:
        print('Marlin codebase directory already exists')

    if os.path.exists(f'{EXTRACONFIG_DIR}/Configuration.h'):
        merge_config(f'{CONFIG_DIR}/config/examples/{CONFIG_BASE}/Configuration.h', f'{EXTRACONFIG_DIR}/Configuration.h', f'{MARLIN_DIR}/Marlin/Configuration.h')
    else:
        shutil.copy(f'{CONFIG_DIR}/config/examples/{CONFIG_BASE}/Configuration.h', f'{MARLIN_DIR}/Marlin')

    if os.path.exists(f'{EXTRACONFIG_DIR}/Configuration_adv.h'):
        merge_config(f'{CONFIG_DIR}/config/examples/{CONFIG_BASE}/Configuration_adv.h', f'{EXTRACONFIG_DIR}/Configuration_adv.h', f'{MARLIN_DIR}/Marlin/Configuration_adv.h')
    else:
        shutil.copy(f'{CONFIG_DIR}/config/examples/{CONFIG_BASE}/Configuration_adv.h', f'{MARLIN_DIR}/Marlin')
    


#
# Build the codebase using platformio
#
def build_codebase():
    os.system(f'~/.platformio/penv/bin/platformio run -d {MARLIN_DIR}')
    
    if not os.path.exists('./Build'):
        os.mkdir('./Build')

    shutil.copy(f'{MARLIN_DIR}/.pio/build/BIGTREE_BTT002/firmware.bin', './Build/firmware.bin')



#
# Set PlatformIO environment
#
def set_environment():
    sed(r'default_envs = .*', 'default_envs = BIGTREE_BTT002', PLATFORMIO_INI, '#')



#
# Info
#
def set_info():
    currentdate = datetime.datetime.today().strftime('%Y-%m-%d')

    sed(r'#define STRING_CONFIG_H_AUTHOR .*', '#define STRING_CONFIG_H_AUTHOR "Prusa Research"', CONFIGURATION_H)
    sed(r'.*#define CUSTOM_VERSION_FILE.*', f'\n#define STRING_DISTRIBUTION_DATE "{currentdate}"', CONFIGURATION_H)
    sed(r'.*#define STRING_DISTRIBUTION_DATE.*', f'#define STRING_DISTRIBUTION_DATE "{currentdate}"\n#define SHORT_BUILD_VERSION "2.0.x"', CONFIGURATION_H)
    sed(r'.*#define CUSTOM_MACHINE_NAME .*', f'#define CUSTOM_MACHINE_NAME "Prusa MK3S+"', CONFIGURATION_H)



#
# Set extra safety
#
def set_safety():
    sed(r'#define HEATER_0_MAXTEMP.*', '#define HEATER_0_MAXTEMP 275', CONFIGURATION_H)
    sed(r'#define BED_MAXTEMP.*', '#define BED_MAXTEMP      100', CONFIGURATION_H)

    sed(r'#define TEMP_WINDOW.*', '#define TEMP_WINDOW              3  // (°C) Temperature proximity for the "temperature reached" timer', CONFIGURATION_H)
    sed(r'#define TEMP_HYSTERESIS.*', '#define TEMP_HYSTERESIS          8  // (°C) Temperature proximity considered "close enough" to the target', CONFIGURATION_H)
    sed(r'#define TEMP_BED_WINDOW.*', '#define TEMP_BED_WINDOW          3  // (°C) Temperature proximity for the "temperature reached" timer', CONFIGURATION_H)
    sed(r'#define TEMP_BED_HYSTERESIS.*', '#define TEMP_BED_HYSTERESIS      8  // (°C) Temperature proximity considered "close enough" to the target', CONFIGURATION_H)

    sed('//#define HOTEND_IDLE_TIMEOUT.*', '#define HOTEND_IDLE_TIMEOUT', CONFIGURATION_ADV_H)

    sed(r'#define Z_MIN_POS.*', '#define Z_MIN_POS 0.15', CONFIGURATION_H) 

    sed(r'.*#define EXPECTED_PRINTER_CHECK', '#define EXPECTED_PRINTER_CHECK', CONFIGURATION_ADV_H)
    sed(r'.*#define NO_MOTION_BEFORE_HOMING', '#define NO_MOTION_BEFORE_HOMING // Inhibit movement until all axes have been homed. Also enable HOME_AFTER_DEACTIVATE for extra safety.', CONFIGURATION_H)
    sed(r'.*#define HOME_AFTER_DEACTIVATE', '#define HOME_AFTER_DEACTIVATE   // Require rehoming after steppers are deactivated. Also enable NO_MOTION_BEFORE_HOMING for extra safety.', CONFIGURATION_H)




#
# Set probing options
#
def set_probing():
    sed(r'#define PROBING_MARGIN.*', '#define PROBING_MARGIN 20', CONFIGURATION_H)
    sed(r'.*#define GRID_MAX_POINTS_X.*', '#define GRID_MAX_POINTS_X 4', CONFIGURATION_H)
    sed(r'#define MULTIPLE_PROBING.*', '#define MULTIPLE_PROBING 3', CONFIGURATION_H)
    sed(r'.*#define EXTRA_PROBING.*', '//#define EXTRA_PROBING    1', CONFIGURATION_H)

    sed(r'#define XY_PROBE_FEEDRATE.*', '#define XY_PROBE_FEEDRATE (133*60)', CONFIGURATION_H)
    sed(r'.*#define Z_AFTER_PROBING.*', '#define Z_AFTER_PROBING           20 // Z position after probing is done', CONFIGURATION_H)



#
# Set homing options
#
def set_homing():
    sed(r'#define HOMING_FEEDRATE_MM_M.*', '#define HOMING_FEEDRATE_MM_M { (50*60), (50*60), (10*60) }', CONFIGURATION_H)
    sed(r'.*#define Z_AFTER_HOMING.*', '#define Z_AFTER_HOMING  20      // (mm) Height to move to after homing Z', CONFIGURATION_H)

    sed(r'#define HOMING_BUMP_MM.*', '#define HOMING_BUMP_MM      { 0, 0, 2 }       // (mm) Backoff from endstops after first bump', CONFIGURATION_ADV_H) # 0, 0, 2



#
# Set other features
#
def set_features():
    # disable arc support
    sed(r'.*#define ARC_SUPPORT .*', '//#define ARC_SUPPORT                 // Disable this feature to save ~3226 bytes', CONFIGURATION_ADV_H)

    # disable s-curve acceleration
    sed(r'.*#define S_CURVE_ACCELERATION.*', '//#define S_CURVE_ACCELERATION', CONFIGURATION_H)
    sed(r'.*#define EXPERIMENTAL_SCURVE.*', '  //#define EXPERIMENTAL_SCURVE   // Enable this option to permit S-Curve Acceleration', CONFIGURATION_ADV_H)

    # disable power loss recovery
    sed(r'.*#define POWER_LOSS_RECOVERY.*', '//#define POWER_LOSS_RECOVERY', CONFIGURATION_ADV_H)

    # nozzle parking
    sed(r'.*#define NOZZLE_PARK_FEATURE', '#define NOZZLE_PARK_FEATURE', CONFIGURATION_H)
    sed(r'.*#define NOZZLE_PARK_POINT.*', '  #define NOZZLE_PARK_POINT { 10, 200, 50 }', CONFIGURATION_H)
    sed(r'.*#define NOZZLE_PARK_Z_FEEDRATE.*', '  #define NOZZLE_PARK_Z_FEEDRATE   10   // (mm/s) Z axis feedrate (not used for delta printers)', CONFIGURATION_H)
    sed(r'.*#define EVENT_GCODE_SD_ABORT.*', '#define EVENT_GCODE_SD_ABORT "G27P2"', CONFIGURATION_ADV_H)

    # for octoprint
    sed(r'.*#define HOST_ACTION_COMMANDS', '#define HOST_ACTION_COMMANDS', CONFIGURATION_ADV_H)
    sed(r'.*#define HOST_PROMPT_SUPPORT', '  #define HOST_PROMPT_SUPPORT', CONFIGURATION_ADV_H)

    # print counter
    sed(r'.*#define PRINTCOUNTER', '#define PRINTCOUNTER', CONFIGURATION_H)



#
# Set lcd
#
def set_lcd():
    sed(r'#define LCD_INFO_SCREEN_STYLE.*', '#define LCD_INFO_SCREEN_STYLE 0', CONFIGURATION_H)
    sed(r'.*#define BOOTSCREEN_TIMEOUT.*', '#define BOOTSCREEN_TIMEOUT 4000      // (ms) Total Duration to display the boot screen(s)', CONFIGURATION_ADV_H)

    sed(r'.*#define BABYSTEP_MULTIPLICATOR_Z .*', '  #define BABYSTEP_MULTIPLICATOR_Z  5       // (steps or mm) Steps or millimeter distance for each Z babystep', CONFIGURATION_ADV_H)
    sed(r'.*#define BABYSTEP_MULTIPLICATOR_XY .*', '  #define BABYSTEP_MULTIPLICATOR_XY 5       // (steps or mm) Steps or millimeter distance for each XY babystep',  CONFIGURATION_ADV_H)

    sed(r'.*#define SHOW_REMAINING_TIME', '  #define SHOW_REMAINING_TIME       // Display estimated time to completion', CONFIGURATION_ADV_H)
    sed(r'.*#define ROTATE_PROGRESS_DISPLAY .*', '    #define ROTATE_PROGRESS_DISPLAY    // Display (P)rogress, (E)lapsed, and (R)emaining time', CONFIGURATION_ADV_H)
    sed(r'.*#define USE_M73_REMAINING_TIME.*', '    #define USE_M73_REMAINING_TIME  // Use remaining time from M73 command instead of estimation', CONFIGURATION_ADV_H)
    sed(r'.*#define LCD_SET_PROGRESS_MANUALLY', '  #define LCD_SET_PROGRESS_MANUALLY', CONFIGURATION_ADV_H)

    sed(r'^    //#define LCD_PROGRESS_BAR.*', '    #define LCD_PROGRESS_BAR            // Show a progress bar on HD44780 LCDs for SD printing', CONFIGURATION_ADV_H)



#
# Set some convenience options
#
def set_convenience():
    sed(r'.*#define BROWSE_MEDIA_ON_INSERT.*', '  #define BROWSE_MEDIA_ON_INSERT          // Open the file browser when media is inserted', CONFIGURATION_ADV_H)
    sed(r'.*#define SDSORT_GCODE.*', '    #define SDSORT_GCODE       true  // Allow turning sorting on/off with LCD and M34 G-code.', CONFIGURATION_ADV_H)



#
# Set hardware specific options
#
def set_hardware():
    sed(r'#define DEFAULT_AXIS_STEPS_PER_UNIT.*', '#define DEFAULT_AXIS_STEPS_PER_UNIT   { 100, 100, 400, 420 }', CONFIGURATION_H)
    sed(r'.*#define E0_MICROSTEPS.*', '    #define E0_MICROSTEPS    16', CONFIGURATION_ADV_H)

    sed(r'.*#define X_STALL_SENSITIVITY.*', '    #define X_STALL_SENSITIVITY  90', CONFIGURATION_ADV_H)
    sed(r'.*#define Y_STALL_SENSITIVITY.*', '    #define Y_STALL_SENSITIVITY  100', CONFIGURATION_ADV_H)

    sed(r'.*#define ADAPTIVE_STEP_SMOOTHING.*', '//#define ADAPTIVE_STEP_SMOOTHING', CONFIGURATION_ADV_H)
    sed(r'.*#define SQUARE_WAVE_STEPPING.*', '  //#define SQUARE_WAVE_STEPPING', CONFIGURATION_ADV_H)

    sed(r'.*#define CHOPPER_TIMING CHOPPER_DEFAULT_24V.*', '  #define CHOPPER_TIMING CHOPPER_PRUSAMK3_24V        // All axes (override below)', CONFIGURATION_ADV_H)

    sed(r'.*#define FLASH_EEPROM_EMULATION.*', '  //#define FLASH_EEPROM_EMULATION                  // Use Flash-based EEPROM emulation', PINS)



#
# Main function
#
if __name__ == '__main__':
    load_codebase()
    set_environment()
    
    set_info()

    set_safety()
    set_homing()
    set_probing()
    set_features()
    set_lcd()
    set_convenience()
    set_hardware()

    build_codebase()
