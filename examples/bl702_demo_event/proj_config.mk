#
#compiler flag config domain
#

#
#board config domain
#


#
#app specific config domain
#

CONFIG_CHIP_NAME := BL702

CONFIG_USE_STDLIB_MALLOC := 0
CONFIG_COEX_ENABLE := 1

CONFIG_USB_CDC := 1

#CONFIG_LINK_RAM := 1
CONFIG_BUILD_ROM_CODE := 1

#CONFIG_DBG_RUN_ON_FPGA := 1
#CONFIG_LINK_CUSTOMER := 1

# set easyflash env psm size, only support 4K、8K options
CONFIG_ENABLE_PSM_EF_SIZE:=4K

CONFIG_USE_PSRAM := 0

# use internal RC32K by default; may set to 1 for better accuracy if there is XTAL32K on the board
CONFIG_USE_XTAL32K := 0

ifeq ($(CFG_BLE_PDS),1)
# use XTAL32K by default for pds31
CONFIG_USE_XTAL32K := 1
endif

# if CONFIG_PDS_CPU_PWROFF is defined, CONFIG_LINK_CUSTOMER must be defined to avoid linking the default .ld file
ifeq ($(CONFIG_PDS_CPU_PWROFF),1)
CONFIG_LINK_CUSTOMER := 1
endif

ifeq ($(CONFIG_SIMPLE_MASTER),1)
CONFIG_LINK_CUSTOMER := 1
endif


ifeq ($(CONFIG_USB_CDC),1)
CONFIG_BL702_USE_USB_DRIVER := 1
endif

CONFIG_BL702_USE_ROM_DRIVER := 1

LOG_ENABLED_COMPONENTS := hosal vfs

CONF_ENABLE_COREDUMP:=1