close all;
clc; clear;
% %%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%% save laplacian of full body %%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%whole body laplacian
file_path = '../dataset/dog0';
M = load_off(file_path);
[W, Sc, Sl] = calc_LB_FEM_bc(M, 'dirichlet');

%save W
file_path_w = [file_path, '_laplacian_W.txt'];
dlmwrite(file_path_w, full(W), 'delimiter','\t');
type(file_path_w);

%save A
file_path_A = [file_path, '_laplacian_A.txt'];
dlmwrite(file_path_A, full(Sc), 'delimiter','\t');
type(file_path_A);

%save A
file_path_A = [file_path, '_laplacian_A_half.txt'];
dlmwrite(file_path_A, full(power(Sc, -0.5)), 'delimiter','\t');
type(file_path_A);



%%%%%%%%%%%%%%%%%%%%%%%%%%%%% save laplacian of small body %%%%%%%%%%%%%%%%%%%%%%%%%%%%%
small_body_file_path = [file_path, '_small_body'];
M = load_off(small_body_file_path);
[W,Sc,Sl] = calc_LB_FEM_bc(M, 'dirichlet');

%save W
file_path_w = [small_body_file_path, '_laplacian_W.txt'];
dlmwrite(file_path_w, full(W), 'delimiter','\t');
type(file_path_w);

%save A
file_path_A = [small_body_file_path, '_laplacian_A.txt'];
dlmwrite(file_path_A, full(Sc), 'delimiter','\t');
type(file_path_A);

%save A_inv
file_path_A_inv = [small_body_file_path, '_laplacian_A_inv.txt'];
dlmwrite(file_path_A_inv, full(inv(Sc)), 'delimiter','\t');
type(file_path_A_inv);

[V, D] = eigs(W, Sc, 20, 'smallestreal');