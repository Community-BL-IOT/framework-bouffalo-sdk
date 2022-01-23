# Copyright 2021-present Maximilian Gerahrdt <maximilian.gerhardt@rub.de>
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
from os.path import isfile, isdir, join

from platformio.util import get_systype

from SCons.Script import COMMAND_LINE_TARGETS, DefaultEnvironment

env = DefaultEnvironment()
platform = env.PioPlatform()
board_config = env.BoardConfig()
board_name = env.subst("$BOARD")

FRAMEWORK_DIR = platform.get_package_dir("framework-bouffalo-sdk")
assert isdir(FRAMEWORK_DIR)

mcu = board_config.get("build.mcu", "")
upload_protocol = env.subst("$UPLOAD_PROTOCOL")

def get_arduino_board_id(board_config, mcu):
    if env.subst("$BOARD") == "pinecone":
        return "PINECONE_EVB"

board_id = get_arduino_board_id(board_config, mcu)

# from platform.txt
sdk = {"version": "release_bl_iot_sdk_1.6.32-104-g52434dce6-dirty",
       "phy_ver": "a0_final-74-g478a1d5", "rf_ver": "0a5bc1d"}

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
    CPPDEFINES=[
        ("F_CPU", "$BOARD_F_CPU"),
        "BL602",
        "CONF_USER_ENABLE_PSRAM",
        "configUSE_TICKLESS_IDLE=0",
        "CFG_FREERTOS",
        "ARCH_RISCV",
        "BL602",
        "CONFIG_SET_TX_PWR",
        "CFG_BLE_ENABLE",
        "BFLB_BLE",
        "CFG_BLE",
        "CFG_SLEEP",
        "OPTIMIZE_DATA_EVT_FLOW_FROM_CONTROLLER",
        ("CFG_CON", 2),
        ("CFG_BLE_TX_BUFF_DATA", 2),
        "CONFIG_BT_ALLROLES",
        "CONFIG_BT_CENTRAL",
        "CONFIG_BT_OBSERVER",
        "CONFIG_BT_PERIPHERAL",
        "CONFIG_BT_BROADCASTER",
        "CONFIG_BT_L2CAP_DYNAMIC_CHANNEL",
        "CONFIG_BT_GATT_CLIENT",
        "CONFIG_BT_CONN",
        "CONFIG_BT_GATT_DIS_PNP",
        "CONFIG_BT_GATT_DIS_SERIAL_NUMBER",
        "CONFIG_BT_GATT_DIS_FW_REV",
        "CONFIG_BT_GATT_DIS_HW_REV",
        "CONFIG_BT_GATT_DIS_SW_REV",
        "CONFIG_BT_ECC",
        "CONFIG_BT_GATT_DYNAMIC_DB",
        "CONFIG_BT_GATT_SERVICE_CHANGED",
        "CONFIG_BT_KEYS_OVERWRITE_OLDEST",
        "CONFIG_BT_KEYS_SAVE_AGING_COUNTER_ON_P",
        "CONFIG_BT_GAP_PERIPHERAL_PREF_PARAMS",
        "CONFIG_BT_BONDABLE",
        "CONFIG_BT_HCI_VS_EVT_USER",
        "CONFIG_BT_ASSERT",
        "CONFIG_BT_SMP",
        "CONFIG_BT_SIGNING",
        "CONFIG_BT_SETTINGS_CCC_LAZY_LOADING",
        "CONFIG_BT_SETTINGS_USE_PRINTK",
        "CFG_BLE_STACK_DBG_PRINT",
        ("BL_SDK_VER", f"{sdk['version']}"),
        ("BL_SDK_PHY_VER", f"{sdk['phy_ver']}"),
        ("BL_SDK_RF_VER", f"{sdk['rf_ver']}"),
        ("BL_CHIP_NAME", "BL602"),
        "ARCH_RISCV",
        ("CONFIG_PSM_EASYFLASH_SIZE", 16384),
        ("configUSE_TICKLESS_IDLE", 0),
        "CFG_BLE_ENABLE",
        "CONF_USER_ENABLE_PSRAM",
        "CONF_USER_ENABLE_VFS_ROMFS",
        ("CFG_COMPONENT_BLOG_ENABLE", 0)
    ],
    CPPPATH=[
        join(FRAMEWORK_DIR, "components", "platform", "soc", "bl602", "bl602"),
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

cpp_defines = env.Flatten(env.get("CPPDEFINES", []))

# copy CCFLAGS to ASFLAGS (-x assembler-with-cpp mode)
env.Append(ASFLAGS=env.get("CCFLAGS", [])[:])

#
# Target: Build Core Library
#

libs = []

env.Prepend(LIBS=libs)
