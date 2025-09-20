//ejercicio 1

#include <stdint.h>
#include <stdbool.h>
#include "inc/hw_memmap.h"
#include "inc/hw_ints.h"
#include "driverlib/sysctl.h"
#include "driverlib/gpio.h"
#include "driverlib/interrupt.h"
#include "driverlib/timer.h"

static uint32_t g_sysClkHz;

// --- Prototipos de ISR “reales” ---
void Timer0AIntHandler(void);

// --- Puentes para coincidir con startup_gcc.c ---
void Timer0IntHandler(void) { Timer0AIntHandler(); }
void Timer1IntHandler(void) { /* no usado, evita undefined reference */ }

static void set_interval_seconds(double seconds) {
    uint32_t load = (uint32_t)(g_sysClkHz * seconds) - 1u;
    TimerDisable(TIMER0_BASE, TIMER_A);
    TimerLoadSet(TIMER0_BASE, TIMER_A, load);
    TimerIntClear(TIMER0_BASE, TIMER_TIMA_TIMEOUT); // por si quedó pendiente
    TimerEnable(TIMER0_BASE, TIMER_A);
}

void Timer0AIntHandler(void) {
    // Limpiar bandera de interrupción
    TimerIntClear(TIMER0_BASE, TIMER_TIMA_TIMEOUT);

    // Toggle PN1
    uint8_t val = GPIOPinRead(GPIO_PORTN_BASE, GPIO_PIN_1);
    GPIOPinWrite(GPIO_PORTN_BASE, GPIO_PIN_1, (val ? 0 : GPIO_PIN_1));
}

int main(void) {
    // 120 MHz con PLL (cristal 25 MHz)
    g_sysClkHz = SysCtlClockFreqSet(
        (SYSCTL_XTAL_25MHZ | SYSCTL_OSC_MAIN | SYSCTL_USE_PLL | SYSCTL_CFG_VCO_480),
        120000000);

    // GPIO N (LEDs) y J (botones)
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPION);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOJ);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPION));
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOJ));

    // PN1 como salida (LED)
    GPIOPinTypeGPIOOutput(GPIO_PORTN_BASE, GPIO_PIN_1);
    GPIOPinWrite(GPIO_PORTN_BASE, GPIO_PIN_1, 0);

    // PJ0 y PJ1 entrada con pull-up
    GPIOPinTypeGPIOInput(GPIO_PORTJ_BASE, GPIO_PIN_0 | GPIO_PIN_1);
    GPIOPadConfigSet(GPIO_PORTJ_BASE, GPIO_PIN_0 | GPIO_PIN_1,
                     GPIO_STRENGTH_2MA, GPIO_PIN_TYPE_STD_WPU);

    // Timer0A periódico con interrupción
    SysCtlPeripheralEnable(SYSCTL_PERIPH_TIMER0);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_TIMER0));
    TimerDisable(TIMER0_BASE, TIMER_A);
    TimerConfigure(TIMER0_BASE, TIMER_CFG_PERIODIC);
    TimerIntClear(TIMER0_BASE, TIMER_TIMA_TIMEOUT);
    TimerIntEnable(TIMER0_BASE, TIMER_TIMA_TIMEOUT);
    IntEnable(INT_TIMER0A);
    IntMasterEnable();

    // Intervalo inicial: 1 s
    set_interval_seconds(1.0);

    // Cambia 1s → 2s → 5s con PJ0
    enum { S_1=0, S_2, S_5 } stage = S_1;
    while (1) {
        uint32_t btns = GPIOPinRead(GPIO_PORTJ_BASE, GPIO_PIN_0 | GPIO_PIN_1);
        bool p0 = (btns & GPIO_PIN_0) == 0; // pulsado = 0
        if (p0) {
    if (stage == S_1) { set_interval_seconds(2.0); stage = S_2; }
    else if (stage == S_2) { set_interval_seconds(5.0); stage = S_5; }
    else { set_interval_seconds(1.0); stage = S_1; }

    // Espera a que SUELTES el botón (active-low)
    do {
        SysCtlDelay(g_sysClkHz/300);   // ~10 ms de debounce (SysCtlDelay=3*N ciclos)
    } while ((GPIOPinRead(GPIO_PORTJ_BASE, GPIO_PIN_0) & GPIO_PIN_0) == 0);
}
    }
}

