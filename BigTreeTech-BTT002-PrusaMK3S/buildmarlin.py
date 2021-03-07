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

MODIFICATION_TAG = 'RTMOD'

MARLIN_REPO = 'https://github.com/rtheuns/Marlin'
MARLIN_BRANCH = 'bugfix-2.0.x'

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
    print('Configuring info')

    currentdate = datetime.datetime.today().strftime('%Y-%m-%d')

    sed(r'.*#define CUSTOM_VERSION_FILE.*', f'\n#define STRING_DISTRIBUTION_DATE "{currentdate}"', CONFIGURATION_H)
    sed(r'.*#define STRING_DISTRIBUTION_DATE.*', f'#define STRING_DISTRIBUTION_DATE "{currentdate}"\n#define SHORT_BUILD_VERSION "{currentdate}"', CONFIGURATION_H)
    sed(r'.*#define CUSTOM_MACHINE_NAME .*', f'#define CUSTOM_MACHINE_NAME "Original Prusa MK3S+"', CONFIGURATION_H)



#
# Main function
#
if __name__ == '__main__':
    load_codebase()
    set_environment()
    set_info()

    set_sheets_feature()

    build_codebase()
