use super::Constraint;

#[derive(Copy, Clone)]
/// A Euclidean sphere, that is, a set given by $B_2^r = \\{x \in \mathbb{R}^n {}:{} \Vert{}x{}\Vert = r\\}$
/// or a Euclidean sphere centered at a point $x_c$, that is, $B_2^{x_c, r} = \\{x \in \mathbb{R}^n {}:{} \Vert{}x-x_c{}\Vert = r\\}$
pub struct Sphere2<'a> {
    center: Option<&'a [f64]>,
    radius: f64,
}

impl<'a> Sphere2<'a> {
    /// Construct a new Euclidean sphere with given center and radius
    /// If no `center` is given, then it is assumed to be in the origin
    pub fn new(center: Option<&'a [f64]>, radius: f64) -> Self {
        assert!(radius > 0.0);
        Sphere2 { center, radius }
    }
}

impl<'a> Constraint for Sphere2<'a> {
    fn project(&self, x: &mut [f64]) {
        if let Some(center) = &self.center {
            let mut norm_difference = 0.0;
            x.iter().zip(center.iter()).for_each(|(xi, ci)| {
                let diff_ = *xi - *ci;
                norm_difference += diff_ * diff_
            });
            norm_difference = norm_difference.sqrt();
            x.iter_mut().zip(center.iter()).for_each(|(x, c)| {
                *x = *c + self.radius * (*x - *c) / norm_difference;
            });
        } else {
            let norm_x = crate::matrix_operations::norm2(x);
            let norm_over_radius = norm_x / self.radius;
            x.iter_mut().for_each(|x_| *x_ /= norm_over_radius);
        }
    }

    fn is_convex(&self) -> bool {
        false
    }
}
