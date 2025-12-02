//*****************************************************************************
// blinky_counter.c - LEDs PN1/PN0/PF4/PF0 muestran un contador 0..15.
// Botones: PJ0 (++), PJ1 (--). EK-TM4C1294XL (TM4C1294NCPDT).
//*****************************************************************************

#include <stdint.h>
#include <stdbool.h>

#include "inc/hw_memmap.h"
#include "driverlib/sysctl.h"
#include "driverlib/gpio.h"
#include "driverlib/debug.h"

// Si compilas con DEBUG, TivaWare pide este manejador:
#ifdef DEBUG
void __error__(char *pcFile, uint32_t ui32Line) {
    while(1);
}
#endif

// Mapeo de LEDs de la placa: D1=PN1, D2=PN0, D3=PF4, D4=PF0
static const uint32_t selector[4] = { GPIO_PORTN_BASE, GPIO_PORTN_BASE, GPIO_PORTF_BASE, GPIO_PORTF_BASE };
static const uint8_t  pins[4]  = { GPIO_PIN_1,      GPIO_PIN_0,      GPIO_PIN_4,      GPIO_PIN_0      };

int main(void)
{
    uint32_t sysclk = SysCtlClockFreqSet(
        SYSCTL_OSC_MAIN | SYSCTL_USE_PLL | SYSCTL_XTAL_25MHZ | SYSCTL_CFG_VCO_320,
        120000000UL
    );

    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPION);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOF);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOJ);

    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPION)) {}
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOF)) {}
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOJ)) {}

    for (int i = 0; i < 4; i++) {
        GPIOPinTypeGPIOOutput(selector[i], pins[i]);
        GPIOPinWrite(selector[i], pins[i], 0); 
    }
    GPIOPinTypeGPIOInput(GPIO_PORTJ_BASE, GPIO_PIN_0 | GPIO_PIN_1);
    GPIOPadConfigSet(GPIO_PORTJ_BASE, GPIO_PIN_0 | GPIO_PIN_1,
                     GPIO_STRENGTH_2MA, GPIO_PIN_TYPE_STD_WPU);

    uint32_t counter = 0;

    while (1) {
        bool sw1 = (GPIOPinRead(GPIO_PORTJ_BASE, GPIO_PIN_0) & GPIO_PIN_0) == 0;
        bool sw2 = (GPIOPinRead(GPIO_PORTJ_BASE, GPIO_PIN_1) & GPIO_PIN_1) == 0;

        if (sw1 && counter < 15) {
            counter++;
            SysCtlDelay(sysclk / 30); 
        }
        if (sw2 && counter > 0) {
            counter--;
            SysCtlDelay(sysclk / 30);
        }

        for (int j = 0; j < 4; j++) {
			
            uint8_t bit = (counter >> j) & 1;
            if (bit) {
                GPIOPinWrite(selector[j], pins[j], pins[j]);
            } else {
                GPIOPinWrite(selector[j], pins[j], 0);
            }
        }

    }
}
