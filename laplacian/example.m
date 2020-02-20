M = load_off('903.off');

[W,Sc,Sl] = calc_LB_FEM_bc(M, 'dirichlet');