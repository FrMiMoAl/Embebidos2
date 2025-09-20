

//ejercicio 3



// p4.c — Decimal (PN0/PN1) con cambio de periodo 2.0 → 1.0 → 0.5 s con PJ0
#include <stdint.h>
#include <stdbool.h>
#include "inc/hw_memmap.h"
#include "inc/hw_ints.h"
#include "driverlib/sysctl.h"
#include "driverlib/gpio.h"
#include "driverlib/interrupt.h"
#include "driverlib/timer.h"

static uint32_t g_sysClkHz;
static volatile uint8_t g_cnt = 0;  // 0..3
static double g_period = 2.0;       // periodo activo

// ISR real + “puentes” para startup_gcc.c
void Timer0AIntHandler(void);
void Timer0IntHandler(void) { Timer0AIntHandler(); }
void Timer1IntHandler(void) { /* no usado */ }

static void set_interval_seconds(double seconds) {
    g_period = seconds;
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
    g_cnt = (g_cnt + 1) & 0x03;      // 0..3
    show_count_on_leds(g_cnt);
}

int main(void) {
    // Reloj 120 MHz (cristal 25 MHz)
    g_sysClkHz = SysCtlClockFreqSet(
        SYSCTL_XTAL_25MHZ | SYSCTL_OSC_MAIN | SYSCTL_USE_PLL | SYSCTL_CFG_VCO_480,
        120000000);

    // GPIO N (PN0/PN1) y J (PJ0 botón con pull-up)
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPION);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOJ);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPION));
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOJ));

    GPIOPinTypeGPIOOutput(GPIO_PORTN_BASE, GPIO_PIN_0 | GPIO_PIN_1);
    GPIOPinWrite(GPIO_PORTN_BASE, GPIO_PIN_0 | GPIO_PIN_1, 0);

    GPIOPinTypeGPIOInput(GPIO_PORTJ_BASE, GPIO_PIN_0);
    GPIOPadConfigSet(GPIO_PORTJ_BASE, GPIO_PIN_0,
                     GPIO_STRENGTH_2MA, GPIO_PIN_TYPE_STD_WPU); // pull-up

    // Timer0A periódico + interrupciones
    SysCtlPeripheralEnable(SYSCTL_PERIPH_TIMER0);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_TIMER0));
    TimerDisable(TIMER0_BASE, TIMER_A);
    TimerConfigure(TIMER0_BASE, TIMER_CFG_PERIODIC);
    TimerIntClear(TIMER0_BASE, TIMER_TIMA_TIMEOUT);
    TimerIntEnable(TIMER0_BASE, TIMER_TIMA_TIMEOUT);
    IntEnable(INT_TIMER0A);
    IntMasterEnable();

    // Periodo inicial: 2 s
    set_interval_seconds(2.0);

    // Detectar flanco en PJ0 (active-low) y ciclar el periodo 2.0→1.0→0.5→2.0
    bool p0_prev = false; // false= no pulsado (porque leeremos ya normalizado)
    while (1) {
        bool p0_now = ((GPIOPinRead(GPIO_PORTJ_BASE, GPIO_PIN_0) & GPIO_PIN_0) == 0);
        if (p0_now && !p0_prev) {
            if (g_period == 2.0) set_interval_seconds(1.0);
            else if (g_period == 1.0) set_interval_seconds(0.5);
            else set_interval_seconds(2.0);
            SysCtlDelay(g_sysClkHz/300); // ~10 ms antirrebote
        }
        p0_prev = p0_now;
    }
}
