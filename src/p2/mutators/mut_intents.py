"""Semantic failure intent strings for each (PUT, primary MP) cell.

Each entry describes what kind of plausible scientific computing defect
the generator should inject, without mentioning any MR.
"""

INTENTS: dict[str, dict] = {
    "a1": {
        "scientific_domain": "Lorenz ODE system solved with RK45",
        "mut_intent": (
            "Introduce a subtle error in the initial conditions or ODE parameter "
            "(sigma, rho, or beta) that plausibly alters the trajectory shape. "
            "The ODE should still integrate without crashing."
        ),
    },
    "a2": {
        "scientific_domain": "LU decomposition of a 2×2 parameterised matrix",
        "mut_intent": (
            "Corrupt the matrix construction or the diagonal-product computation "
            "so that the returned scalar is numerically wrong but still finite. "
            "Example defects: wrong off-diagonal entry, wrong diagonal multiplier, "
            "using sum instead of product."
        ),
    },
    "a3": {
        "scientific_domain": "Explicit Euler finite-difference heat equation (1D)",
        "mut_intent": (
            "Alter the finite-difference stencil, the time-step formula, or the "
            "boundary conditions so that the numerical solution is wrong while the "
            "code still runs. The scheme should still resemble a plausible FDM implementation."
        ),
    },
    "b1": {
        "scientific_domain": "Beta-Binomial conjugate Bayesian update",
        "mut_intent": (
            "Modify the posterior parameter update so that the posterior mean does "
            "not correctly reflect the observed successes. Example: swap alpha and "
            "beta, use wrong prior, compute mode instead of mean."
        ),
    },
    "b2": {
        "scientific_domain": "Metropolis-Hastings MCMC targeting a Gaussian",
        "mut_intent": (
            "Change the target distribution specification, acceptance criterion, "
            "or chain initialisation so that the chain mean drifts away from the "
            "true target mean. The MCMC loop must still run and return a float."
        ),
    },
    "b3": {
        "scientific_domain": "Monte Carlo integration of ∫₀¹(x+t²)dt",
        "mut_intent": (
            "Perturb the integrand formula or the sample-based estimator so that "
            "the linearity property (estimate shifts by exactly c when x shifts by c) "
            "is violated. Keep the function runnable."
        ),
    },
    "c1": {
        "scientific_domain": "Gaussian Process Regression surrogate for erf(t)",
        "mut_intent": (
            "Alter the GPR training data range, kernel hyperparameters, or the "
            "prediction call so that the surrogate output no longer faithfully "
            "tracks the monotone target function."
        ),
    },
    "c2": {
        "scientific_domain": "Polynomial Chaos Expansion surrogate for tanh(t)",
        "mut_intent": (
            "Modify the training points, polynomial degree, or regressor fit so "
            "that the PCE output deviates from the true monotone function in a "
            "plausible way."
        ),
    },
    "c3": {
        "scientific_domain": "MLP neural network surrogate for sigmoid(2t)",
        "mut_intent": (
            "Change the network architecture, training data, or activation so that "
            "the NN output loses the monotone fidelity relationship with the target."
        ),
    },
    "d1": {
        "scientific_domain": "Linear SVM binary classifier",
        "mut_intent": (
            "Alter the feature vector construction or the training labels so that "
            "P(y=1) does not monotonically increase with x along the designed "
            "input path."
        ),
    },
    "d2": {
        "scientific_domain": "RBF SVM binary classifier",
        "mut_intent": (
            "Modify the feature mapping or the decision boundary training so that "
            "the predicted probability P(y=1) loses its monotone relationship with x."
        ),
    },
    "d3": {
        "scientific_domain": "Decision Tree binary classifier",
        "mut_intent": (
            "Change the feature construction or tree training so that the decision "
            "tree's predicted probability P(y=1) no longer follows a monotone "
            "pattern with x."
        ),
    },
}
