// Study-5 Family-XL adapter shim (pair: tanh.rs). Adapter/oracle layer only:
// the external file is copied VERBATIM to ext.rs by the build adapter.
#![allow(dead_code)]
use std::io::{self, BufRead, Write};

#[path = "ext.rs"]
mod ext;
fn program(x: f64) -> f64 {
    let mut v: Vec<f32> = vec![(4.0 * x - 2.0) as f32];
    ext::tanh(&mut v);
    v[0] as f64
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
