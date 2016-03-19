/**
  ******************************************************************************
  * File Name          : main.c
  * Description        : Main program body
  ******************************************************************************
  *
  * COPYRIGHT(c) 2016 STMicroelectronics
  *
  * Redistribution and use in source and binary forms, with or without modification,
  * are permitted provided that the following conditions are met:
  *   1. Redistributions of source code must retain the above copyright notice,
  *      this list of conditions and the following disclaimer.
  *   2. Redistributions in binary form must reproduce the above copyright notice,
  *      this list of conditions and the following disclaimer in the documentation
  *      and/or other materials provided with the distribution.
  *   3. Neither the name of STMicroelectronics nor the names of its contributors
  *      may be used to endorse or promote products derived from this software
  *      without specific prior written permission.
  *
  * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
  * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
  * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
  * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
  * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
  * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
  * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
  * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
  * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
  * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
  *
  ******************************************************************************
  */
/* Includes ------------------------------------------------------------------*/
#include "stm32f3xx_hal.h"
#include "i2c.h"
#include "gpio.h"

/* USER CODE BEGIN Includes */
#include <stdbool.h>
/* USER CODE END Includes */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
/* Private variables ---------------------------------------------------------*/
#define I2C_BUFFER_SIZE	64

#define MESSAGE_START	0x1B
#define TOKEN			0x0E

#define CMD_CHIP_ERASE	0x12

#define STATUS_CMD_OK	0x00

static volatile uint32_t i2cErrorCounter;
static volatile uint32_t i2cReceiveFlag;
static uint8_t i2cRxCharacter[I2C_BUFFER_SIZE];
static uint8_t i2cTxCharacter[I2C_BUFFER_SIZE];
static volatile uint16_t i2cRxLength;
static volatile uint16_t i2cTxLength;

static uint8_t st_sequence_number;
static uint16_t st_message_size;

static uint32_t eraseAddress;


/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);

/* USER CODE BEGIN PFP */
/* Private function prototypes -----------------------------------------------*/
static uint8_t calculateSTK500Checksum(uint8_t *buffer, uint16_t length);
static void build_response_buffer(uint8_t responseCommand, uint8_t responseValue);
static void buildMessageHeader(uint16_t length);
static bool processRequest(void);
static bool commandProcessor(uint8_t *commandBuffer, uint16_t size);
static bool processEraseRequest(uint8_t *commandBuffer, uint16_t size);
/* USER CODE END PFP */

/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

int main(void)
{

  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration----------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* Configure the system clock */
  SystemClock_Config();

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_I2C1_Init();
  MX_I2C2_Init();

  /* USER CODE BEGIN 2 */
  i2cErrorCounter = 0;
  i2cReceiveFlag = 0;
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */

  // --
  // -- Start the I2C receive function.
  // --
  HAL_I2C_Slave_Receive_IT(&hi2c1, i2cRxCharacter, sizeof(i2cRxCharacter));

  while (1)
  {
  /* USER CODE END WHILE */

  /* USER CODE BEGIN 3 */
	  if(i2cReceiveFlag)
	  {
		  if(true == processRequest())
		  {
			  HAL_I2C_Slave_Transmit_IT(&hi2c1, i2cTxCharacter, i2cTxLength);
		  }


		  //
		  // Restart I2C Receiving
		  // Clear the receive flag first
		  //
		  i2cReceiveFlag = 0;
		  HAL_I2C_Slave_Receive_IT(&hi2c1, i2cRxCharacter, sizeof(i2cRxCharacter));

	  }

  }
  /* USER CODE END 3 */

}

/** System Clock Configuration
*/
void SystemClock_Config(void)
{

  RCC_OscInitTypeDef RCC_OscInitStruct;
  RCC_ClkInitTypeDef RCC_ClkInitStruct;
  RCC_PeriphCLKInitTypeDef PeriphClkInit;

  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL9;
  RCC_OscInitStruct.PLL.PREDIV = RCC_PREDIV_DIV1;
  HAL_RCC_OscConfig(&RCC_OscInitStruct);

  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;
  HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2);

  PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_I2C1|RCC_PERIPHCLK_I2C2
                              |RCC_PERIPHCLK_TIM20;
  PeriphClkInit.I2c1ClockSelection = RCC_I2C1CLKSOURCE_SYSCLK;
  PeriphClkInit.I2c2ClockSelection = RCC_I2C2CLKSOURCE_SYSCLK;
  PeriphClkInit.Tim20ClockSelection = RCC_TIM20CLK_HCLK;
  HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit);

  HAL_SYSTICK_Config(HAL_RCC_GetHCLKFreq()/1000);

  HAL_SYSTICK_CLKSourceConfig(SYSTICK_CLKSOURCE_HCLK);

  /* SysTick_IRQn interrupt configuration */
  HAL_NVIC_SetPriority(SysTick_IRQn, 0, 0);
}

/* USER CODE BEGIN 4 */

/**
 * Function: processRequest
 *
 * Input:
 * 	 None
 *
 * Output:
 * 	None
 *
 * Returns:
 * 	true - Response is ready to send
 * 	false - No response required
 *
 * Description:
 * 	Verifies the checksum on the current request. If no errors
 * 	are detected, save the sequence number, extract the data
 * 	segment of the request, and pass the request to the command
 * 	processor.
 */
static bool processRequest(void)
{
	uint8_t bufferChecksum;
	bool responseFlag;



	if(MESSAGE_START != i2cRxCharacter[0])
	{
		return false;
	}

	// --
	// -- Calculate the checksum in the buffer. i2cRxLength is
	// -- set by the i2c interrupt service routine
	// --
	bufferChecksum = calculateSTK500Checksum(i2cRxCharacter, i2cRxLength-1);

	responseFlag = false;

	if( (bufferChecksum == i2cRxCharacter[i2cRxLength-1]) && (TOKEN == i2cRxCharacter[4]))
	{
		st_sequence_number = i2cRxCharacter[1];
		st_message_size = ((uint16_t)i2cRxCharacter[2] << 8) + (uint16_t)i2cRxCharacter[3];
		responseFlag = commandProcessor(&i2cRxCharacter[5], st_message_size);
	}

	return responseFlag;
}

/**
 * Function: commandProcessor
 *
 * Input:
 * 	commandBuffer - Block containing request command
 * 	size - Number of bytes int he request
 *
 * Output:
 * 	None
 *
 * Returns:
 * 	None
 *
 * Description:
 * 	Routes requests to the appropriate command processing function
 */
static bool commandProcessor(uint8_t *commandBuffer, uint16_t size)
{
	bool responseFlag;
	switch(commandBuffer[0])
	{
	case CMD_CHIP_ERASE:
		responseFlag = processEraseRequest(commandBuffer, size);
		break;
	default:
		responseFlag = false;
		break;
	}
	return responseFlag;
}


static bool processEraseRequest(uint8_t *commandBuffer, uint16_t size)
{
	eraseAddress = 0;

	build_response_buffer(CMD_CHIP_ERASE, STATUS_CMD_OK);

	return true;
}


/**
 * Function: calculateSTK500Checksum
 *
 * Input:
 * 	buffer - Pointer to buffer containing source data
 * 	length - Number of bytes in the source data buffer
 *
 * Output:
 * 	None
 *
 * Returns:
 * 	XOR checksum based on source buffer
 */
static uint8_t calculateSTK500Checksum(uint8_t *buffer, uint16_t length)
{
	uint16_t index;
	uint8_t checksum;
	checksum = buffer[0];
	for(index=1; index<length; index++)
	{
		checksum ^= buffer[index];
	}
	return checksum;
}

/**
 * Function: build_response_buffer
 *
 * Input:
 * 	responseCommand: command response is generated for
 * 	responseValue: Pass / Fail indicator for response
 *
 * Output:
 * 	None
 *
 * Returns:
 * 	none
 *
 * Description:
 * 	This function simply builds an STK500 response packet.
 * 	The response will be returned to the host on the next TWI read
 * 	request.
 */
static void build_response_buffer(uint8_t responseCommand, uint8_t responseValue)
{
	buildMessageHeader(2);
	i2cTxCharacter[5] = responseCommand;
	i2cTxCharacter[6] = responseValue;
	i2cTxCharacter[7] = calculateSTK500Checksum(i2cTxCharacter, 7);

	i2cTxLength = 8;
}

static void buildMessageHeader(uint16_t length)
{
	i2cTxCharacter[0] = MESSAGE_START;
	i2cTxCharacter[1] = st_sequence_number;
	i2cTxCharacter[2] = (length >> 8);
	i2cTxCharacter[3] = (length & 0x00FF);
	i2cTxCharacter[4] = TOKEN;
}

void HAL_I2C_SlaveRxCpltCallback(I2C_HandleTypeDef *hi2c)
{
	i2cReceiveFlag++;
	i2cRxLength = (I2C_BUFFER_SIZE - hi2c->XferCount);

}

void HAL_I2C_ErrorCallback(I2C_HandleTypeDef *hi2c)
{
	i2cErrorCounter++;
}


/* USER CODE END 4 */

#ifdef USE_FULL_ASSERT

/**
   * @brief Reports the name of the source file and the source line number
   * where the assert_param error has occurred.
   * @param file: pointer to the source file name
   * @param line: assert_param error line source number
   * @retval None
   */
void assert_failed(uint8_t* file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
    ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */

}

#endif

/**
  * @}
  */ 

/**
  * @}
*/ 

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
