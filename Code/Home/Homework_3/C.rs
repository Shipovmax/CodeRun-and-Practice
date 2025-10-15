use std::io;

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    let mut tokens = input.split_whitespace();

    let n: usize = tokens.next().unwrap().parse().unwrap();
    let W: f64 = tokens.next().unwrap().parse().unwrap();
    let H: f64 = tokens.next().unwrap().parse().unwrap();

    let mut a = Vec::with_capacity(n);
    let mut b = Vec::with_capacity(n);

    for _ in 0..n {
        let ai: f64 = tokens.next().unwrap().parse().unwrap();
        let bi: f64 = tokens.next().unwrap().parse().unwrap();
        a.push(ai);
        b.push(bi);
    }

    let mut low = 0.0;
    let mut high = 1e9 + 1.0;

    for _ in 0..100 {
        let mid = (low + high) / 2.0;
        if feasible(mid, &a, &b, W, H) {
            low = mid;
        } else {
            high = mid;
        }
    }

    println!("{:.10}", low);
}

fn feasible(k: f64, a: &[f64], b: &[f64], W: f64, H: f64) -> bool {
    let mut current_width = 0.0;
    let mut current_b = -1.0;
    let mut total_height = 0.0;

    for i in 0..a.len() {
        let w = k * a[i];
        if w > W {
            return false;
        }

        if current_b == -1.0 {
            current_width = w;
            current_b = b[i];
        } else {
            if current_b == b[i] && current_width + w <= W {
                current_width += w;
            } else {
                total_height += k * current_b;
                if total_height > H {
                    return false;
                }
                current_width = w;
                current_b = b[i];
            }
        }
    }

    total_height += k * current_b;
    total_height <= H
}
