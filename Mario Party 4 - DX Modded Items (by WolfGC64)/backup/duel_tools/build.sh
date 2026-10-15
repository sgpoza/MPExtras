set -e
/private/tmp/claude-501/-Users-sgpoza-Documents-Decomp-marioparty4/1cb775f1-1fdc-4b10-bb05-edd15e77e95a/scratchpad/zig cc -target powerpc-freestanding-eabihf -mcpu=750 -mhard-float -Os -g0 -fno-pic -ffreestanding -fno-builtin -fno-jump-tables -fomit-frame-pointer -fno-asynchronous-unwind-tables -fno-unwind-tables -Wall -Wno-unused-function -c duel.c -o duel.o
/private/tmp/claude-501/-Users-sgpoza-Documents-Decomp-marioparty4/1cb775f1-1fdc-4b10-bb05-edd15e77e95a/scratchpad/zig cc -target powerpc-freestanding-eabihf -nostdlib -Wl,-T,link.ld -Wl,--no-gc-sections -o duel.elf duel.o
