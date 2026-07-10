// Study-5 Family-XL adapter shim (pair: trapezoid.rs). Adapter/oracle layer only:
// the external file is copied VERBATIM to ext.rs by the build adapter.
#![allow(dead_code)]
use std::io::{self, BufRead, Write};

#[path = "ext.rs"]
mod ext;
fn program(x: f64) -> f64 {
    let c = 2.0_f64.powf(2.0 * x - 1.0);
    ext::trapezoidal_integral(0.0, c, |u| u * u, 64)
}

fn main() {
    let stdin = io::stdin();
    let stdout = io::stdout();
    let mut out = stdout.lock();
    for line in stdin.lock().lines() {
        let line = match line { Ok(l) => l, Err(_) => break };
        let s = line.trim();
        if s.is_empty() { continue; }
        let x: f64 = match s.parse() { Ok(v) => v, Err(_) => continue };
        let y: f64 = program(x);
        writeln!(out, "{:.17e}", y).ok();
        out.flush().ok();
    }
}
