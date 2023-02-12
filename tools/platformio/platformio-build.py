# Copyright 2021-present Maximilian Gerahrdt <maximilian.gerhardt@rub.de>
#                        Joe Saiko <joe@saiko.dev>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Written by Maximilian Gerhardt <maximilian.gerhardt@rub.de>
# for the Pine64 Bouffalo BL602 core.

"""


"""

import json
import sys
import time

from os.path import isfile, isdir, join
from platformio.util import get_systype
from SCons.Script import COMMAND_LINE_TARGETS, DefaultEnvironment

# Init
env = DefaultEnvironment()
platform = env.PioPlatform()
board_config = env.BoardConfig()
board_name = env.subst("$BOARD")

FRAMEWORK_DIR = platform.get_package_dir("framework-bouffalo-sdk")
assert isdir(FRAMEWORK_DIR)

# Read sdk-data.json
try:
    SDKDATA = json.load(open(join(FRAMEWORK_DIR, 'sdk-data.json')))
except ValueError as err:
    sys.exit("Error reading " + join(FRAMEWORK_DIR, "sdk-data.json"))

# Determine chip name
bl_chipname = SDKDATA['boards'][board_name]['chipname']

# Get build components
try:
    COMPONENTS = env.GetProjectOption("include_components").split()
except:
    COMPONENTS = SDKDATA['sdk']['defaults']['components']

# Print Info
print("BOUFFALO SDK:")
print(" - Version: " + SDKDATA['sdk']['version'])
print(" - Chip: " + bl_chipname)
print(" - Components: " + ", ".join(COMPONENTS))

#
# Setup Default Build Env
#
include_dirs = []
defines = SDKDATA['sdk']['defaults']['defines']

# iterate through default include dirs and prepend framework path
for x in range(0, len(SDKDATA['sdk']['defaults']['include_dirs'])):
    include_dirs.append(join(FRAMEWORK_DIR, SDKDATA['sdk']['defaults']['include_dirs'][x]))

def define_val(txt):
    for x in range(0, len(defines)):
        stmt = defines[x]
        if isinstance(stmt, list):
            if(stmt[0] == txt):
                return stmt[1]
        else:
            if(stmt == txt):
                return True
    return False

def eval_conditionals(branch):
    for eval in branch:
        statement = eval.split()
        first_statement = statement[0] 
        if first_statement == 'ifeq':
            svalue = define_val(statement[1])
            if svalue == statement[2]:
                print("CONDITION MET (" + statement[1] + "):" + str(svalue))
                if 'include_dirs' in branch:
                    include_dirs += branch['include_dirs']
        elif first_statement == 'ifdef':
            svalue = define_val(statement[1])
            if svalue != False:
                print("CONDITION MET (" + statement[1] + "):" + str(svalue))
                if 'include_dirs' in branch:
                    include_dirs += branch['include_dirs']
        elif first_statement == 'ifndef':
            svalue = define_val(statement[1])
            if svalue == False:
                print("CONDITION MET (" + statement[1] + "):" + str(svalue))
                if 'include_dirs' in branch:
                    include_dirs += branch['include_dirs']
        else:
            print("WARNING: invalid conditional statement")


# add package specific includes and definitions
for i in range(len(COMPONENTS)):
    # select specific hosal build
    if COMPONENTS[i] == "hosal":
        COMPONENTS[i] = "hosal-" + bl_chipname

    if COMPONENTS[i] in SDKDATA['components']:
        defines += SDKDATA['components'][COMPONENTS[i]]['defines']
        include_dirs += SDKDATA['components'][COMPONENTS[i]]['include_dirs']

        # TODO: Eval conditionals
        if 'conditionals' in SDKDATA['components'][COMPONENTS[i]]:
            eval_conditionals(SDKDATA['components'][COMPONENTS[i]]['conditionals'])

env.Append(
    ASFLAGS=["-x", "assembler-with-cpp"],
    CFLAGS=["-std=gnu99"],
    CXXFLAGS=[
        "-std=gnu++11",
        "-fno-use-cxa-atexit", 
        "-nostdlib", 
        "-Wpointer-arith", 
        "-fexceptions", 
        "-fstack-protector", 
        "-fno-rtti", 
        "-fno-exceptions", 
        "-fms-extensions", 
        "-Werror=return-type"
    ],
    CCFLAGS=[
        "-Os",  # optimize for size
        "-Wall",  # show warnings
        "-march=%s" % board_config.get("build.march"),
        "-mabi=%s" % board_config.get("build.mabi"),
        #"-nostdlib",
        "-gdwarf", 
        "-ffunction-sections",
        "-fdata-sections",
        "-fstrict-volatile-bitfields",
        "-fshort-enums",
        "-ffreestanding",
        "-fno-strict-aliasing",
        "--param",
        "max-inline-insns-single=500",
    ],
    CPPDEFINES = defines + [
        "ARCH_RISCV",
        ("BL_SDK_VER", "\\\"" + f"{SDKDATA['sdk']['version']}" + "\\\""),
        ("BL_SDK_PHY_VER", "\\\"" + f"{SDKDATA['sdk']['phy_ver']}" + "\\\""),
        ("BL_SDK_RF_VER", "\\\"" + f"{SDKDATA['sdk']['rf_ver']}" + "\\\""),
        ("F_CPU", "$BOARD_F_CPU"),
        bl_chipname,
        ("BL_CHIP_NAME", bl_chipname),
        ("CONFIG_PSM_EASYFLASH_SIZE", 16384),
        ("__FILENAME__", "\\\"fixme.c\\\""),
        ("BFLB_COREDUMP_BINARY_ID", time.time())
    ],
    CPPPATH = include_dirs + [
        #join(FRAMEWORK_DIR, "components", "platform", "soc", "bl602", "bl602_std", "bl602_std", "Common", "libc", "inc")
    ],
    LINKFLAGS=[
        "-Os",
        "-march=%s" % board_config.get("build.march"),
        "-mabi=%s" % board_config.get("build.mabi"),
        "-nostartfiles",
        "-Wl,--gc-sections,--relax",
        "-Wl,--check-sections",
        "-Wl,--unresolved-symbols=report-all",
        "-Wl,--warn-common",
        "-Wl,--defsym=LD_MAX_SIZE=%d" % board_config.get("upload.maximum_size"),
        "-Wl,--defsym=LD_MAX_DATA_SIZE=%d" % board_config.get("upload.maximum_ram_size"),
        "-Wl,-static"
    ],
    LIBS=[
        "c",
        "m",
        "gcc",
        "stdc++",
        "wifi",
        "blecontroller_602_std"
    ],
    LIBPATH=[
        join(FRAMEWORK_DIR, "components", "network", "wifi", "lib"),
        join(FRAMEWORK_DIR, "components", "network", "ble", "blecontroller_602_std", "lib"),
    ]
)

#
# Linker requires preprocessing with correct RAM|ROM sizes
#
env.Replace(LDSCRIPT_PATH=join(
                    FRAMEWORK_DIR,
                    "components",
                    "platform",
                    "soc",
                    "bl602",
                    "bl602",
                    "evb",
                    "ld",
                    "flash_rom.ld"
                ))

#
# Process configuration flags
#

# copy CCFLAGS to ASFLAGS (-x assembler-with-cpp mode)
env.Append(ASFLAGS=env.get("CCFLAGS", [])[:])

#
# Target: Build Core Library
#
libs = []

# Iterate through components definitions
def find_component_conf(name):
    result = None
    for component_x in SDKDATA['components']:
        if name == component_x:
            result = SDKDATA['components'][component_x]
            break
    return result

# Iterate through included components and build libraries
for x in COMPONENTS:
    component = find_component_conf(x)
    if component is None:
        print("***WARNING: Undefined component (" + x + ")")
        continue

    # iterate through default include dirs and prepend framework path
    include_dirs_priv = []
    for y in range(0, len(component['include_dirs_priv'])):
        include_dirs_priv.append(join(FRAMEWORK_DIR, component['include_dirs_priv'][y]))

    # Clone and set up component build env
    env_c = env.Clone()
    env_c.Append(
        CPPPATH=include_dirs_priv
    )
    # TODO: Evaluate conditionals

    # Eval source filter
    if isinstance(component['source_filter'], list):
        source_filter = " ".join(component['source_filter'])
    else:
        source_filter = component['source_filter']

    # Build library
    libs.append(env_c.BuildLibrary(join("$BUILD_DIR", x), join(FRAMEWORK_DIR, component['source_dir']), source_filter))


env.Prepend(LIBS=libs)

