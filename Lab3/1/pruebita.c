//*****************************************************************************
//
// blinky.c - Simple example to blink the on-board LED.
//
// Copyright (c) 2013-2017 Texas Instruments Incorporated.  All rights reserved.
// Software License Agreement
// 
// Texas Instruments (TI) is supplying this software for use solely and
// exclusively on TI's microcontroller products. The software is owned by
// TI and/or its suppliers, and is protected under applicable copyright
// laws. You may not combine this software with "viral" open-source
// software in order to form a larger program.
// 
// THIS SOFTWARE IS PROVIDED "AS IS" AND WITH ALL FAULTS.
// NO WARRANTIES, WHETHER EXPRESS, IMPLIED OR STATUTORY, INCLUDING, BUT
// NOT LIMITED TO, IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
// A PARTICULAR PURPOSE APPLY TO THIS SOFTWARE. TI SHALL NOT, UNDER ANY
// CIRCUMSTANCES, BE LIABLE FOR SPECIAL, INCIDENTAL, OR CONSEQUENTIAL
// DAMAGES, FOR ANY REASON WHATSOEVER.
// 
// This is part of revision 2.1.4.178 of the EK-TM4C1294XL Firmware Package.
//
//*****************************************************************************

#include <stdint.h>
#include <stdbool.h>
#include "inc/hw_memmap.h"
#include "driverlib/debug.h"
#include "driverlib/gpio.h"
#include "driverlib/sysctl.h"


//*****************************************************************************
//
//! \addtogroup example_list
//! <h1>Blinky (blinky)</h1>
//!
//! A very simple example that blinks the on-board LED using direct register
//! access.
//
//*****************************************************************************

//*****************************************************************************
//
// The error routine that is called if the driver library encounters an error.
//
//*****************************************************************************
#ifdef DEBUG
void
__error__(char *pcFilename, uint32_t ui32Line)
{
    while(1);
}
#endif

//*****************************************************************************
//
// Blink the on-board LED.
//
//*****************************************************************************
int
main(void)
{
    volatile uint32_t ui32Loop;

    //
    // Enable the GPIO port that is used for the on-board LED.
    //
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPION);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPION))
    {}
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOF);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOF)) {}
    
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOJ);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOJ)) {}

    // leds
    GPIOPinTypeGPIOOutput(GPIO_PORTN_BASE, GPIO_PIN_0);
    GPIOPinTypeGPIOOutput(GPIO_PORTN_BASE, GPIO_PIN_1);
    GPIOPinTypeGPIOOutput(GPIO_PORTF_BASE, GPIO_PIN_0);
    GPIOPinTypeGPIOOutput(GPIO_PORTF_BASE, GPIO_PIN_4);
    
    
    GPIOPinTypeGPIOInput(GPIO_PORTJ_BASE, GPIO_PIN_0 | GPIO_PIN_1);
    GPIOPadConfigSet(GPIO_PORTJ_BASE,GPIO_PIN_0 | GPIO_PIN_1,GPIO_STRENGTH_2MA,GPIO_PIN_TYPE_STD_WPU);
    
    const uint8_t pinsN[] = { GPIO_PIN_1, GPIO_PIN_0 };
    
    const uint8_t pinsF[] = { GPIO_PIN_4, GPIO_PIN_0 };
    const uint8_t maskN   = GPIO_PIN_0 | GPIO_PIN_1;
    const uint8_t maskF   = GPIO_PIN_0 | GPIO_PIN_4;
    
    

    
    
    
    //
    // Loop forever.
    //
    while(1)
    {
        bool push1 = (GPIOPinRead(GPIO_PORTJ_BASE, GPIO_PIN_0) & GPIO_PIN_0) == 0;
	bool push2 = (GPIOPinRead(GPIO_PORTJ_BASE, GPIO_PIN_1) & GPIO_PIN_1) == 0;


	if(push1){
		for (int i =0; i<2;i++){
    			GPIOPinWrite(GPIO_PORTN_BASE, pinsN[i], pinsN[i]);
		for(ui32Loop = 0; ui32Loop < 2000000; ui32Loop++){
        	}
    		}
    		for (int i =0;i<2;i++){
    			GPIOPinWrite(GPIO_PORTF_BASE, pinsF[i], pinsF[i]);
		for(ui32Loop = 0; ui32Loop < 2000000; ui32Loop++){
        	}
    		}
    		GPIOPinWrite(GPIO_PORTN_BASE, maskN, 0);
                GPIOPinWrite(GPIO_PORTF_BASE, maskF, 0);	
	}
	
    	else if(push2){
    		GPIOPinWrite(GPIO_PORTN_BASE, maskN, maskN);
                GPIOPinWrite(GPIO_PORTF_BASE, maskF, maskF);
	    	for (int k=1; k>=0;k--){
	    		GPIOPinWrite(GPIO_PORTF_BASE, pinsF[k], 0x0);
			for(ui32Loop = 0; ui32Loop < 2000000; ui32Loop++)
			{
			}
	    	}
	    	for (int j=1; j>=0;j--){
	    		GPIOPinWrite(GPIO_PORTN_BASE, pinsN[j], 0x0);
			for(ui32Loop = 0; ui32Loop < 2000000; ui32Loop++)
			{
			}
	    	}
        
    	}else {
            // Sin botones: todo apagado
            GPIOPinWrite(GPIO_PORTN_BASE, maskN, 0);
            GPIOPinWrite(GPIO_PORTF_BASE, maskF, 0);
        }
}
}
