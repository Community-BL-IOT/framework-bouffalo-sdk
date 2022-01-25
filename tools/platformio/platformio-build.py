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

# Get build components
include_components = env.GetProjectOption("include_components")
COMPONENTS = include_components.split()
print("COMPONENTS: " + ", ".join(COMPONENTS))

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
        ("BL_SDK_VER", "\\\"" + f"{sdk['version']}" + "\\\""),
        ("BL_SDK_PHY_VER", "\\\"" + f"{sdk['phy_ver']}" + "\\\""),
        ("BL_SDK_RF_VER", "\\\"" + f"{sdk['rf_ver']}" + "\\\""),
        ("BL_CHIP_NAME", "BL602"),
        "ARCH_RISCV",
        ("CONFIG_PSM_EASYFLASH_SIZE", 16384),
        ("configUSE_TICKLESS_IDLE", 0),
        "CFG_BLE_ENABLE",
        "CONF_USER_ENABLE_PSRAM",
        "CONF_USER_ENABLE_VFS_ROMFS",
        ("CFG_COMPONENT_BLOG_ENABLE", 0),
        ("SYS_APP_TASK_STACK_SIZE", 4096),
        ("SYS_APP_TASK_PRIORITY", 15),
        ("portasmHANDLE_INTERRUPT", "interrupt_entry"),
        "LWIP_ENABLED",
        "CONFIG_PLAT_AOS",
        "BFLB_CRYPT_HARDWARE"
    ],
    CPPPATH=[
        join(FRAMEWORK_DIR, "components", "fs", "vfs"),
        join(FRAMEWORK_DIR, "components", "fs", "vfs", "include"),
        join(FRAMEWORK_DIR, "components", "fs", "vfs", "posix", "include"),
        join(FRAMEWORK_DIR, "components", "platform", "soc", "bl602", "bl602"),
        join(FRAMEWORK_DIR, "components", "platform", "soc", "bl602", "bl602", "include"),
        join(FRAMEWORK_DIR, "components", "platform", "soc", "bl602", "bl602_std"),
        join(FRAMEWORK_DIR, "components", "platform", "soc", "bl602", "bl602_std", "include"),
        join(FRAMEWORK_DIR, "components", "platform", "soc", "bl602", "bl602_std", "bl602_std", "StdDriver", "Inc"),
        join(FRAMEWORK_DIR, "components", "platform", "soc", "bl602", "bl602_std", "bl602_std", "Device", "Bouffalo", "BL602", "Peripherals"),
        join(FRAMEWORK_DIR, "components", "platform", "soc", "bl602", "bl602_std", "bl602_std", "RISCV", "Device", "Bouffalo", "BL602", "Startup"),
        join(FRAMEWORK_DIR, "components", "platform", "soc", "bl602", "bl602_std", "bl602_std", "RISCV", "Core", "Include"),
        join(FRAMEWORK_DIR, "components", "platform", "soc", "bl602", "bl602_std", "bl602_std", "Include"),
        join(FRAMEWORK_DIR, "components", "platform", "soc", "bl602", "bl602_std", "bl602_std", "Common", "platform_print"),
        join(FRAMEWORK_DIR, "components", "platform", "soc", "bl602", "bl602_std", "bl602_std", "Common", "soft_crc"),
        join(FRAMEWORK_DIR, "components", "platform", "soc", "bl602", "bl602_std", "bl602_std", "Common", "partition"),
        join(FRAMEWORK_DIR, "components", "platform", "soc", "bl602", "bl602_std", "bl602_std", "Common", "xz"),
        join(FRAMEWORK_DIR, "components", "platform", "soc", "bl602", "bl602_std", "bl602_std", "Common", "cipher_suite", "inc"),
        join(FRAMEWORK_DIR, "components", "platform", "soc", "bl602", "bl602_std", "bl602_std", "Common", "ring_buffer"),
        join(FRAMEWORK_DIR, "components", "stage", "blfdt"),
        join(FRAMEWORK_DIR, "components", "stage", "blfdt", "include"),
        join(FRAMEWORK_DIR, "components", "stage", "blfdt", "inc"),
        join(FRAMEWORK_DIR, "components", "sys", "blmtd"),
        join(FRAMEWORK_DIR, "components", "sys", "blmtd", "include"),
        join(FRAMEWORK_DIR, "components", "sys", "blmtd", "include"),
        join(FRAMEWORK_DIR, "components", "stage", "blog"),
        join(FRAMEWORK_DIR, "components", "stage", "blog", "include"),
        join(FRAMEWORK_DIR, "components", "stage", "blog"),
        join(FRAMEWORK_DIR, "components", "stage", "blog_testc"),
        join(FRAMEWORK_DIR, "components", "stage", "blog_testc", "include"),
        join(FRAMEWORK_DIR, "components", "stage", "blog_testc"),
        join(FRAMEWORK_DIR, "components", "sys", "bloop", "bloop"),
        join(FRAMEWORK_DIR, "components", "sys", "bloop", "bloop", "include"),
        join(FRAMEWORK_DIR, "components", "sys", "bloop", "bloop", "include"),
        join(FRAMEWORK_DIR, "components", "sys", "bltime"),
        join(FRAMEWORK_DIR, "components", "sys", "bltime", "include"),
        join(FRAMEWORK_DIR, "components", "sys", "bltime", "include"),
        join(FRAMEWORK_DIR, "components", "stage", "cli"),
        join(FRAMEWORK_DIR, "components", "stage", "cli", "include"),
        join(FRAMEWORK_DIR, "components", "stage", "cli", "cli", "include"),
        join(FRAMEWORK_DIR, "components", "stage", "coredump"),
        join(FRAMEWORK_DIR, "components", "stage", "coredump", "include"),
        join(FRAMEWORK_DIR, "components", "stage", "coredump", "inc"),
        join(FRAMEWORK_DIR, "components", "platform", "soc", "bl602", "freertos_riscv_ram"),
        join(FRAMEWORK_DIR, "components", "platform", "soc", "bl602", "freertos_riscv_ram", "include"),
        join(FRAMEWORK_DIR, "components", "platform", "soc", "bl602", "freertos_riscv_ram", "config"),
        join(FRAMEWORK_DIR, "components", "platform", "soc", "bl602", "freertos_riscv_ram", "portable", "GCC", "RISC-V"),
        join(FRAMEWORK_DIR, "components", "platform", "soc", "bl602", "freertos_riscv_ram", "portable", "GCC", "RISC-V", "chip_specific_extensions", "RV32F_float_abi_single"),
        join(FRAMEWORK_DIR, "components", "platform", "soc", "bl602", "freertos_riscv_ram", "panic"),
        join(FRAMEWORK_DIR, "components", "platform", "hosal"),
        join(FRAMEWORK_DIR, "components", "platform", "hosal", "include"),
        join(FRAMEWORK_DIR, "components", "platform", "hosal", "bl602_hal"),
        join(FRAMEWORK_DIR, "components", "platform", "hosal", "platform_hal"),
        join(FRAMEWORK_DIR, "components", "platform", "hosal", "include"),
        join(FRAMEWORK_DIR, "components", "sys", "bloop", "looprt"),
        join(FRAMEWORK_DIR, "components", "sys", "bloop", "looprt", "include"),
        join(FRAMEWORK_DIR, "components", "sys", "bloop", "loopset"),
        join(FRAMEWORK_DIR, "components", "sys", "bloop", "loopset", "include"),
        join(FRAMEWORK_DIR, "components", "libc", "newlibc"),
        join(FRAMEWORK_DIR, "components", "libc", "newlibc", "include"),
        join(FRAMEWORK_DIR, "components", "libc", "newlibc"),
        join(FRAMEWORK_DIR, "components", "fs", "romfs"),
        join(FRAMEWORK_DIR, "components", "fs", "romfs", "include"),
        join(FRAMEWORK_DIR, "components", "utils"),
        join(FRAMEWORK_DIR, "components", "utils", "include"),
        join(FRAMEWORK_DIR, "components", "stage", "yloop"),
        join(FRAMEWORK_DIR, "components", "stage", "yloop", "include"),
        join(FRAMEWORK_DIR, "components", "stage", "yloop", "include"),

        #join(FRAMEWORK_DIR, "components", "platform", "soc", "bl602", "bl602_std", "bl602_std", "Common", "libc", "inc"),

        join(FRAMEWORK_DIR, "components", "security", "mbedtls", "include"),
        join(FRAMEWORK_DIR, "components", "security", "mbedtls", "include", "mbedtls"),
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
