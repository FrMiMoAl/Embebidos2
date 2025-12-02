#******************************************************************************
# Makefile - Rules for building the blinky example (portable).
#******************************************************************************

# MCU
PART=TM4C1294NCPDT

# === Ubicación de TivaWare ===
# Exporta TIVAWARE o TIVAWARE_ROOT antes de compilar, o pon la ruta aquí.
TIVAWARE ?= $(TIVAWARE_ROOT)
# Fallback: intenta usar ROOT si ya está definido externamente
TIVAWARE ?= $(ROOT)

# Si aún no está definida, puedes “hardcodear” tu ruta local aquí:
# TIVAWARE ?= /home/franco/lm4tools/TivaWarePah/SW-TM4C-2.1.4.178

# Comprobación mínima
ifeq ("$(wildcard $(TIVAWARE)/makedefs)","")
$(error No se encontró 'makedefs'. Define TIVAWARE (o TIVAWARE_ROOT) apuntando a la raíz de TivaWare)
endif

# Incluye definiciones comunes de TivaWare
include $(TIVAWARE)/makedefs

# Dirs de include adicionales (opcional)
IPATH += $(TIVAWARE)

# Binario de salida
all: ${COMPILER}
all: ${COMPILER}/pruebita.axf

# Limpieza
clean:
	@rm -rf ${COMPILER} ${wildcard *~}

# Carpeta de build
${COMPILER}:
	@mkdir -p ${COMPILER}

# --- Dependencias y reglas de enlace ---
# Asegura que driverlib esté compilada antes de enlazar
${TIVAWARE}/driverlib/${COMPILER}/libdriver.a:
	$(MAKE) -C ${TIVAWARE}/driverlib

${COMPILER}/pruebita.axf: ${COMPILER}/pruebita.o
${COMPILER}/pruebita.axf: ${COMPILER}/startup_${COMPILER}.o
${COMPILER}/pruebita.axf: ${TIVAWARE}/driverlib/${COMPILER}/libdriver.a
${COMPILER}/pruebita.axf: pruebita.ld

# Script de link y símbolo de entrada
SCATTERgcc_pruebita=pruebita.ld
ENTRY_pruebita=ResetISR

# Flags específicos (ajústalo si usas otra rev del silicio)
CFLAGSgcc+=-DTARGET_IS_TM4C129_RA1

# Dependencias automáticas
ifneq (${MAKECMDGOALS},clean)
-include ${wildcard ${COMPILER}/*.d} __dummy__
endif

