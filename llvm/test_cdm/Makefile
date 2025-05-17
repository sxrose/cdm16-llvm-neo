
CC=../cmake-build-debug-clang/bin/clang
C_OPTS=-target cdm -S -O1

ASM=cocas
ASM_OPTS=-t cdm16

EMU=/home/ilya/work/cdm_clang/cdm-devkit/logisim/logisim-cdm-emulator/standalone/build/libs/standalone-all.jar

out_asm/%.asm: src/%.c $(CC)
	$(CC) $(C_OPTS) -o $@ $+

out_bin/%.bin: out_asm/%.asm start.asm
	$(ASM) $(ASM_OPTS) -o $@ $+

run_%: out_bin/%.bin
	java -jar $(EMU) $+ emu_out/$@.json 1000000000

test:
	pytest -n auto

build/cdm-devkit:
	cd build && git clone git@github.com:cdm-processors/cdm-devkit.git -b 0.2.2

prepare_tests: build/cdm-devkit
	mkdir -p build
	docker build -t cdm-devkit --file config/cdm-devkit.Dockerfile .
	docker run --rm -v ${PWD}/build:/root cdm-devkit make prepare_tests
	mkdir -p build/resources
	cp build/cdm-devkit/tests/jar/logisim-runner-all.jar build/resources/
	cp build/cdm-devkit/tests/resources/cdm16/circuits/* build/resources/

#clean:
#	rm -rv out_asm/*
#	rm -rv out_bin/*
#
#.PHONY: clean
#

.PHONY: run_%
.SECONDARY: