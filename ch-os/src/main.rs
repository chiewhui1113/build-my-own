#![no_std] // Don't link the Rust standard library 
#![no_main] // Disable all Rust-level entry points

mod vga_buffer;

use core::panic::PanicInfo;

static HELLO: &[u8] = b"Hello World!";

#[unsafe(no_mangle)] // Don't mangle the name of this function 
// ! means not allowed to ever return 
// Entry point invoked by the os or bootloader
pub extern "C" fn _start() -> ! {
    // First address that maps to the screen
    let vga_buffer = 0xb8000 as *mut u8;

    for (i, &byte) in HELLO.iter().enumerate() {
        unsafe {
            // Byte 1: character
            *vga_buffer.offset(i as isize * 2) = byte;
            // Byte 2: color
            *vga_buffer.offset(i as isize * 2 + 1) = 0xb;
        }
    }

    // Keeps OS alive
    loop {}
}

// Function called on panic
#[panic_handler]
fn panic(_info: &PanicInfo) -> ! {
    loop {}
}
