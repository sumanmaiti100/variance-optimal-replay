"""Replay buffer.

Identical to the AAAI-era buffer except for one addition required by the state-
distribution correction: a ring store of *initial* states s0. The Liu et al.
(2018a) discounted minimax objective that identifies xi = d^pi/d^b contains the
term (1 - gamma) E_{s0 ~ p0}[(1 - w(s0)) f(s0)], so the estimator needs samples
from the start-state distribution p0, which a flat transition buffer does not
otherwise expose.
"""
import numpy as np
import torch


class ReplayBuffer:
    def __init__(self, obs_dim, act_dim, capacity, device, init_capacity=20_000):
        self.capacity = capacity
        self.device = device
        self.s = np.zeros((capacity, obs_dim), dtype=np.float32)
        self.a = np.zeros((capacity, act_dim), dtype=np.float32)
        self.r = np.zeros((capacity,), dtype=np.float32)
        self.c = np.zeros((capacity,), dtype=np.float32)
        self.s2 = np.zeros((capacity, obs_dim), dtype=np.float32)
        self.done = np.zeros((capacity,), dtype=np.float32)
        self.logp_beh = np.zeros((capacity,), dtype=np.float32)
        self.ptr = 0
        self.size = 0

        # Start-state store for the density-ratio estimator's (1 - gamma) term.
        self.init_capacity = init_capacity
        self.s0 = np.zeros((init_capacity, obs_dim), dtype=np.float32)
        self.init_ptr = 0
        self.n_init = 0

    def add(self, s, a, r, c, s2, done, logp_beh):
        i = self.ptr
        self.s[i] = s; self.a[i] = a; self.r[i] = r; self.c[i] = c
        self.s2[i] = s2; self.done[i] = done; self.logp_beh[i] = logp_beh
        self.ptr = (self.ptr + 1) % self.capacity
        self.size = min(self.size + 1, self.capacity)

    def add_initial(self, s0):
        i = self.init_ptr
        self.s0[i] = s0
        self.init_ptr = (self.init_ptr + 1) % self.init_capacity
        self.n_init = min(self.n_init + 1, self.init_capacity)

    def sample_uniform_idx(self, n):
        return np.random.randint(0, self.size, size=n)

    def sample_initial(self, n):
        idx = np.random.randint(0, max(self.n_init, 1), size=n)
        return torch.as_tensor(self.s0[idx], device=self.device)

    def to_torch(self, idx):
        return (
            torch.as_tensor(self.s[idx], device=self.device),
            torch.as_tensor(self.a[idx], device=self.device),
            torch.as_tensor(self.r[idx], device=self.device),
            torch.as_tensor(self.c[idx], device=self.device),
            torch.as_tensor(self.s2[idx], device=self.device),
            torch.as_tensor(self.done[idx], device=self.device),
            torch.as_tensor(self.logp_beh[idx], device=self.device),
        )
