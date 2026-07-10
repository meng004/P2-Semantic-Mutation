// Study-5 Family-XL adapter shim (pair: newton.rs). Adapter/oracle layer only:
// the external file is copied VERBATIM to ext.rs by the build adapter.
#![allow(dead_code)]
use std::io::{self, BufRead, Write};
use std::sync::atomic::{AtomicU64, Ordering};
#[path = "ext.rs"]
mod ext;
static A: AtomicU64 = AtomicU64::new(0);

fn f(t: f64) -> f64 {
    t * t - f64::from_bits(A.load(Ordering::Relaxed))
}

fn fd(t: f64) -> f64 {
    2.0 * t
}

fn program(x: f64) -> f64 {
    let a = 4.0_f64.powf(2.0 * x - 1.0);
    A.store(a.to_bits(), Ordering::Relaxed);
    ext::find_root(f, fd, 1.5, 8)
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
