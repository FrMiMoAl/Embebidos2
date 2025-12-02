

//ejercicio 2


// p4.c — Decimal sequence 0..3 en PN0/PN1 cada 2 s
#include <stdint.h>
#include <stdbool.h>
#include "inc/hw_memmap.h"
#include "inc/hw_ints.h"
#include "driverlib/sysctl.h"
#include "driverlib/gpio.h"
#include "driverlib/interrupt.h"
#include "driverlib/timer.h"

static uint32_t g_sysClkHz;
static volatile uint8_t g_cnt = 0; // 0..3

// ISR “real”
void Timer0AIntHandler(void);

// Puentes para startup_gcc.c (evitan undefined reference)
void Timer0IntHandler(void) { Timer0AIntHandler(); }
void Timer1IntHandler(void) { /* no usado */ }

static void set_interval_seconds(double seconds) {
    uint32_t load = (uint32_t)(g_sysClkHz * seconds) - 1u;
    TimerDisable(TIMER0_BASE, TIMER_A);
    TimerLoadSet(TIMER0_BASE, TIMER_A, load);
    TimerIntClear(TIMER0_BASE, TIMER_TIMA_TIMEOUT);
    TimerEnable(TIMER0_BASE, TIMER_A);
}

static void show_count_on_leds(uint8_t v) {
    uint8_t out = 0;
    if (v & 0x01) out |= GPIO_PIN_0; // bit0 -> PN0
    if (v & 0x02) out |= GPIO_PIN_1; // bit1 -> PN1
    GPIOPinWrite(GPIO_PORTN_BASE, GPIO_PIN_0 | GPIO_PIN_1, out);
}

void Timer0AIntHandler(void) {
    TimerIntClear(TIMER0_BASE, TIMER_TIMA_TIMEOUT);
    g_cnt = (g_cnt + 1) & 0x03;  // 0..3
    show_count_on_leds(g_cnt);
}

int main(void) {
    // Reloj a 120 MHz
    g_sysClkHz = SysCtlClockFreqSet(
        SYSCTL_XTAL_25MHZ | SYSCTL_OSC_MAIN | SYSCTL_USE_PLL | SYSCTL_CFG_VCO_480,
        120000000);

    // GPIO N (LEDs PN0/PN1)
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPION);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPION));
    GPIOPinTypeGPIOOutput(GPIO_PORTN_BASE, GPIO_PIN_0 | GPIO_PIN_1);
    GPIOPinWrite(GPIO_PORTN_BASE, GPIO_PIN_0 | GPIO_PIN_1, 0); // muestra "0" al inicio

    // Timer0A periódico con interrupción
    SysCtlPeripheralEnable(SYSCTL_PERIPH_TIMER0);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_TIMER0));
    TimerDisable(TIMER0_BASE, TIMER_A);
    TimerConfigure(TIMER0_BASE, TIMER_CFG_PERIODIC);
    TimerIntClear(TIMER0_BASE, TIMER_TIMA_TIMEOUT);
    TimerIntEnable(TIMER0_BASE, TIMER_TIMA_TIMEOUT);
    IntEnable(INT_TIMER0A);
    IntMasterEnable();

    // 2 segundos por paso
    set_interval_seconds(2.0);

    // Nada más que hacer en el lazo; la ISR lleva la secuencia
    while (1) { /* idle */ }
}





