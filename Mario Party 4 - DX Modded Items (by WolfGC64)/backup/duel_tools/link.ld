ENTRY(duel_land)
SECTIONS {
  . = 0;
  .text : { *(.text .text.*) }
  .rodata : { *(.rodata .rodata.* .sdata2 .sdata2.*) }
  .data : { *(.data .data.* .sdata .sdata.* .bss .bss.* .sbss .sbss.*) }
  /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) *(.gnu*) }
}
