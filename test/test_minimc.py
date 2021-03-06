from autograd import grad
import autograd.numpy as np
from numpy.testing import assert_allclose, assert_almost_equal

from minimc import leapfrog, hamiltonian_monte_carlo, neg_log_normal, neg_log_mvnormal


def test_leapfrog():
    neg_log_p = neg_log_normal(2, 0.1)
    dlogp = grad(neg_log_p)
    q, p = np.array(0.0), np.array(2.0)
    path_len, step_size = 1, 0.1

    # Should be reversible
    q_new, p_new = leapfrog(q, p, dlogp, path_len, step_size)
    q_new, p_new = leapfrog(q_new, p_new, dlogp, path_len, step_size)
    assert_almost_equal(q_new, q)
    assert_almost_equal(p_new, p)


def test_leapfrog_mv():
    mu = np.arange(10)
    cov = 0.8 * np.ones((10, 10)) + 0.2 * np.eye(10)
    neg_log_p = neg_log_mvnormal(mu, cov)

    dlogp = grad(neg_log_p)
    q, p = np.zeros(mu.shape), np.ones(mu.shape)
    path_len, step_size = 1, 0.1

    # Should be reversible
    q_new, p_new = leapfrog(q, p, dlogp, path_len, step_size)
    q_new, p_new = leapfrog(q_new, p_new, dlogp, path_len, step_size)
    assert_almost_equal(q_new, q)
    assert_almost_equal(p_new, p)


def test_hamiltonian_monte_carlo():
    # This mostly tests consistency. Tolerance chosen by experiment
    # Do statistical tests on your own time.
    np.random.seed(1)
    neg_log_p = neg_log_normal(2, 0.1)
    samples = hamiltonian_monte_carlo(100, neg_log_p, np.array(0.0))
    assert samples.shape[0] == 100
    assert_allclose(2.0, np.mean(samples), atol=0.02)
    assert_allclose(0.1, np.std(samples), atol=0.007)


def test_hamiltonian_monte_carlo_mv():
    np.random.seed(1)
    mu = np.arange(2)
    cov = 0.8 * np.ones((2, 2)) + 0.2 * np.eye(2)
    neg_log_p = neg_log_mvnormal(mu, cov)

    samples = hamiltonian_monte_carlo(100, neg_log_p, np.zeros(mu.shape), path_len=2.0)
    assert samples.shape[0] == 100
    assert_allclose(mu, np.mean(samples, axis=0), atol=0.13)
    assert_allclose(cov, np.cov(samples.T), atol=0.17)
