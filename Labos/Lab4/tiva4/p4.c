

//ejercicio 4 timers



// EK-TM4C1294XL - Binary counter with Timer0 and button-controlled interval
// - Timer0 genera el "tick" que avanza el contador (wrap 0..15).
// - Intervalo base: 1.5 s. Si SW1 (PJ0) está presionado -> 3.0 s.
// - LEDs: PN1 (bit3), PN0 (bit2), PF4 (bit1), PF0 (bit0)
// - Switches: PJ0 (SW1), PJ1 (SW2) con pull-ups; solo usamos SW1 para el tiempo.

#include <stdint.h>
#include <stdbool.h>
#include "inc/hw_memmap.h"
#include "driverlib/sysctl.h"
#include "driverlib/gpio.h"
#include "driverlib/interrupt.h"
#include "driverlib/timer.h"
#include "inc/hw_ints.h" 

static volatile uint32_t g_sysClkHz;
static volatile int      g_counter = 0;      // 0..15
static volatile uint32_t g_interval_ticks;   // carga actual del timer

// ---- stubs exigidos por startup_gcc.c (en tu entorno pide estos nombres) ----
void Timer0IntHandler(void);   // usaremos este para el Timer0
void Timer1IntHandler(void) { } // vacío (no usado)

// ---- Utilidades ----
static inline uint32_t seconds_to_ticks(double s) {
  // Timer0A en modo periódico con clock del sistema (prescaler por defecto 1)
  double ticks = (double)g_sysClkHz * s;
  if (ticks < 2.0) ticks = 2.0;          // evita underflow al restar 1
  return (uint32_t)(ticks) - 1u;
}

static inline void leds_write(uint8_t v4) {
  uint8_t pn = 0;
  if (v4 & 0x08) pn |= (1U << 1); // PN1
  if (v4 & 0x04) pn |= (1U << 0); // PN0
  GPIOPinWrite(GPIO_PORTN_BASE, GPIO_PIN_0 | GPIO_PIN_1, pn);

  uint8_t pf = 0;
  if (v4 & 0x02) pf |= GPIO_PIN_4;       // PF4
  if (v4 & 0x01) pf |= GPIO_PIN_0;       // PF0
  GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_0 | GPIO_PIN_4, pf);
}

static inline bool sw1_pressed(void) {
  // Activo en bajo (pull-up interno)
  return (GPIOPinRead(GPIO_PORTJ_AHB_BASE, GPIO_PIN_0) == 0);
}

// ---- ISR del Timer0 ----
void Timer0IntHandler(void)
{
  // limpiar la bandera de timeout
  TimerIntClear(TIMER0_BASE, TIMER_TIMA_TIMEOUT);

  // avanzar contador (wrap-around) y actualizar LEDs
  g_counter = (g_counter == 15) ? 0 : (g_counter + 1);
  leds_write((uint8_t)(g_counter & 0x0F));
}

int main(void)
{
  // 1) Reloj a 120 MHz
  g_sysClkHz = SysCtlClockFreqSet(
      SYSCTL_XTAL_25MHZ | SYSCTL_OSC_MAIN | SYSCTL_USE_PLL | SYSCTL_CFG_VCO_240,
      120000000);

  // 2) GPIO para LEDs (N y F) y switches (J AHB)
  SysCtlPeripheralEnable(SYSCTL_PERIPH_GPION);
  SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOF);
  SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOJ);
  while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPION));
  while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOF));
  while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOJ));

  GPIOPinTypeGPIOOutput(GPIO_PORTN_BASE, GPIO_PIN_0 | GPIO_PIN_1);
  GPIOPinTypeGPIOOutput(GPIO_PORTF_BASE, GPIO_PIN_0 | GPIO_PIN_4);

  GPIOPinTypeGPIOInput(GPIO_PORTJ_AHB_BASE, GPIO_PIN_0 | GPIO_PIN_1);
  GPIOPadConfigSet(GPIO_PORTJ_AHB_BASE, GPIO_PIN_0 | GPIO_PIN_1,
                   GPIO_STRENGTH_2MA, GPIO_PIN_TYPE_STD_WPU);

  // Estado inicial de LEDs
  g_counter = 0;
  leds_write((uint8_t)(g_counter & 0x0F));

  // 3) Configurar Timer0A periódico
  SysCtlPeripheralEnable(SYSCTL_PERIPH_TIMER0);
  while(!SysCtlPeripheralReady(SYSCTL_PERIPH_TIMER0));

  TimerDisable(TIMER0_BASE, TIMER_A);
  TimerConfigure(TIMER0_BASE, TIMER_CFG_PERIODIC);

  // intervalo base 1.5 s
  g_interval_ticks = seconds_to_ticks(1.5);
  TimerLoadSet(TIMER0_BASE, TIMER_A, g_interval_ticks);

  // habilitar interrupciones
  TimerIntClear(TIMER0_BASE, TIMER_TIMA_TIMEOUT);
  TimerIntEnable(TIMER0_BASE, TIMER_TIMA_TIMEOUT);
  IntEnable(INT_TIMER0A);          // NVIC
  IntMasterEnable();               // habilita globalmente las IRQ

  TimerEnable(TIMER0_BASE, TIMER_A);

  // 4) Bucle: leer SW1 y ajustar periodo (1.5s / 3.0s mientras está presionado)
  bool last_state = false;
  while (1) {
    bool pressed = sw1_pressed();

    // Soft-debounce simple por cambio
    if (pressed != last_state) {
      // ~5ms de espera (busy-wait barato)
      SysCtlDelay((g_sysClkHz/3/1000) * 5);
      pressed = sw1_pressed();
    }

    // Si el estado (presionado/no presionado) cambió realmente, actualizamos el periodo
    if (pressed != last_state) {
      last_state = pressed;

      double new_sec = pressed ? 3.0 : 1.5;
      uint32_t new_ticks = seconds_to_ticks(new_sec);

      // Actualizamos el periodo de forma segura
      TimerDisable(TIMER0_BASE, TIMER_A);
      g_interval_ticks = new_ticks;
      TimerLoadSet(TIMER0_BASE, TIMER_A, g_interval_ticks);
      TimerIntClear(TIMER0_BASE, TIMER_TIMA_TIMEOUT);
      TimerEnable(TIMER0_BASE, TIMER_A);
    }
    // pequeña espera para no saturar la CPU (≈1ms)
    SysCtlDelay(g_sysClkHz / 3000);
  }
}
