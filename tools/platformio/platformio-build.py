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

# iterate through default include dirs and prepend framework path
include_dirs = []
for x in range(0, len(SDKDATA['sdk']['defaults']['include_dirs'])):
    include_dirs.append(join(FRAMEWORK_DIR, SDKDATA['sdk']['defaults']['include_dirs'][x]))

# add package specific includes
for x in COMPONENTS:
    if x in SDKDATA['components']:
        include_dirs += SDKDATA['components'][x]['include_dirs']

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
    CPPDEFINES = SDKDATA['sdk']['defaults']['defines'] + [
        "ARCH_RISCV",
        ("BL_SDK_VER", "\\\"" + f"{SDKDATA['sdk']['version']}" + "\\\""),
        ("BL_SDK_PHY_VER", "\\\"" + f"{SDKDATA['sdk']['phy_ver']}" + "\\\""),
        ("BL_SDK_RF_VER", "\\\"" + f"{SDKDATA['sdk']['rf_ver']}" + "\\\""),
        ("F_CPU", "$BOARD_F_CPU"),
        bl_chipname,
        ("BL_CHIP_NAME", bl_chipname),
        ("CFG_CON", 2),
        ("CFG_BLE_TX_BUFF_DATA", 2),
        ("CONFIG_PSM_EASYFLASH_SIZE", 16384),
        ("CFG_COMPONENT_BLOG_ENABLE", 0),

        ("portasmHANDLE_INTERRUPT", "interrupt_entry"),
    ],
    CPPPATH=include_dirs,
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
        "wifi"
    ],
    LIBPATH=[
        join(FRAMEWORK_DIR, "components", "network", "wifi", "lib"),
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
# This is unused?
# cpp_defines = env.Flatten(env.get("CPPDEFINES", []))

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

    # Clone and set up component build env
    env_c = env.Clone()
    env_c.Append(
        CPPDEFINES=component['defines']
    )

    # Build library
    libs.append(env_c.BuildLibrary(join("$BUILD_DIR", x), join(FRAMEWORK_DIR, component['source_dir'], component['source_filter'])))

#libs.append(env.BuildLibrary(join("$BUILD_DIR", "freertos_riscv_ram"), join(FRAMEWORK_DIR, "components", "platform", "soc", "bl602", "freertos_riscv_ram")))
#libs.append(env.BuildLibrary(join("$BUILD_DIR", "bl602"), join(FRAMEWORK_DIR, "components", "platform", "soc", "bl602", "bl602")))
#libs.append(env.BuildLibrary(join("$BUILD_DIR", "bl602_std"), join(FRAMEWORK_DIR, "components", "platform", "soc", "bl602", "bl602_std"), src_filter="+<*> -<bl602_std/Common>"))
#libs.append(env.BuildLibrary(join("$BUILD_DIR", "newlibc"), join(FRAMEWORK_DIR, "components", "platform", "soc", "libc", "newlibc")))

#libs.append(env.BuildLibrary(join("$BUILD_DIR", "bl602_hal"), join(FRAMEWORK_DIR, "components", "platform", "hosal", "bl602_hal")))
#libs.append(env.BuildLibrary(join("$BUILD_DIR", "platform_hal"), join(FRAMEWORK_DIR, "components", "platform", "hosal", "platform_hal")))

#libs.append(env.BuildLibrary(join("$BUILD_DIR", "vfs"), join(FRAMEWORK_DIR, "components", "platform", "fs", "vfs")))
#libs.append(env.BuildLibrary(join("$BUILD_DIR", "yloop"), join(FRAMEWORK_DIR, "components", "platform", "stage", "yloop")))
#libs.append(env.BuildLibrary(join("$BUILD_DIR", "utils"), join(FRAMEWORK_DIR, "components", "platform", "utils")))
#libs.append(env.BuildLibrary(join("$BUILD_DIR", "cli"), join(FRAMEWORK_DIR, "components", "platform", "stage", "cli")))
#libs.append(env.BuildLibrary(join("$BUILD_DIR", "blog"), join(FRAMEWORK_DIR, "components", "platform", "stage", "blog")))
#libs.append(env.BuildLibrary(join("$BUILD_DIR", "blog_testc"), join(FRAMEWORK_DIR, "components", "platform", "stage", "blog_testc")))
#libs.append(env.BuildLibrary(join("$BUILD_DIR", "coredump"), join(FRAMEWORK_DIR, "components", "platform", "stage", "coredump")))

#libs.append(env.BuildLibrary(join("$BUILD_DIR", "bltime"), join(FRAMEWORK_DIR, "components", "platform", "sys", "bltime")))
#libs.append(env.BuildLibrary(join("$BUILD_DIR", "blfdt"), join(FRAMEWORK_DIR, "components", "platform", "stage", "blfdt")))
#libs.append(env.BuildLibrary(join("$BUILD_DIR", "blmtd"), join(FRAMEWORK_DIR, "components", "platform", "sys", "blmtd")))
#libs.append(env.BuildLibrary(join("$BUILD_DIR", "bloop"), join(FRAMEWORK_DIR, "components", "platform", "sys", "bloop")))

env.Prepend(LIBS=libs)

