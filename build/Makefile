# Configurações
MCU=atmega328p
PORT=/dev/cu.usbmodem14101
PROGRAMMER=arduino
BAUD=115200

# Nome base do arquivo
TARGET ?= expr_1

# Sem caminhos extras agora
SRC=$(TARGET).asm
HEX=$(TARGET).hex

# Compilar
all: $(HEX)

$(HEX): $(SRC)
	avra -o $(HEX) $(SRC)

# Upload para o Arduino
upload: $(HEX)
	avrdude -V -F -c $(PROGRAMMER) -p $(MCU) -P $(PORT) -b $(BAUD) -U flash:w:$(HEX)

# Limpar arquivos
clean:
	rm -f *.hex *.o

.PHONY: all upload clean
