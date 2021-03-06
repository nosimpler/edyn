#!usr/bin/python
# jacobian.py: Methods to get useful things from the jacobian matrix

# Requires a partition on network nodes (TODO: link partitions.py)
# Allows for a priori computation of parameters guaranteeing 
# synchronization as per e.g. Pham and Slotine (2007; in Neural Networks) 
# or cosynchronization (Law, 2014; PhD thesis)
# Author: Robert Law

from sympy import *
import numpy as np

# Input: zero-indexed partition of network nodes
# Output: unit vectors corresponding to synchrony subspace
def partition_to_units(partition):    
    flatten = lambda l: [item for sublist in l for item in sublist]
    n_cols = len(partition)
    n_rows = len(flatten(partition))
    vec = np.zeros((n_rows, n_cols))
    for i,p in enumerate(partition):
        vec[p,i] = 1 
    return Matrix(vec.astype(int))

# Input: zero-indexed partition of network nodes
# Output: vectors corresponding to cosynchrony (synchrony-null) space 
def partition_to_nulls(partition):
    u = partition_to_units(partition)
    return Matrix.hstack(*u.T.nullspace())

# Input: Jacobian matrix
# Output: Jacobian matrix symmetrized to have real eigenvalues
def symmetrize_jacobian(J):
    J_sym = (J + J.T)/2
    return J_sym

# Input: Collection of vectors (from partition_to_null or
#     partition_to_unit) and
#     Jacobian matrix
# Output: Fibered Jacobian
def reduce_jacobian(colvecs, J):
    new_J = colvecs.T*J*colvecs
    return new_J

# Input: (Fibered) Jacobian matrix
# Output: Set of expressions for Gershgorin discs 
#     These must all be negative for synchronization/cosynchronization
def gershgorin_disc(J):
    sz = J.shape[0]
    new_J = zeros(sz, sz)
    for i in range(sz):
        for j in range(sz):
            if i != j:
                new_J[i,j] = abs(J[i,j])
            else:
                new_J[i,i] = J[i,i]
    return ones(1, sz)*new_J
    

if __name__ == '__main__':
    partition = [[0,1],[2,3]]
    u = partition_to_units(partition)
    n = partition_to_nulls(partition)
    vars = Matrix(["v_1", "v_2", "u_1", "u_2"])
    params = ["w_1", "w_2", "a_1", "a_2", "b_1", "b_2", 'tau_1', 'tau_2']
    ODE_sys = Matrix(["v_1-(v_1**3)/3 - u_1 + w_1*v_2",
                "v_2-(v_2**3)/3 - u_2 + w_2*v_1",
                "a_1*(b_1*v_1 - u_1)",
                "a_2*(b_2*v_2 - u_2)"])
    J = ODE_sys.jacobian(vars)
    J_reduced_u = reduce_jacobian(u,J)
    J_sym_u = symmetrize_jacobian(J_reduced_u)
    J_reduced_n = reduce_jacobian(n,J)
    J_sym_n = symmetrize_jacobian(J_reduced_n)
print("Synchronization conditions:", gershgorin_disc(J_sym_u))
print("Cosynchronization conditions:", gershgorin_disc(J_sym_n))

