close all;
clc; clear;
%% load data
addpath('/laplacian');
file_path = './dataset/dog0';
X = load_off(file_path);
[W_X, ~, Sc_X] = calc_LB_FEM_bc(X, 'dirichlet');

%% cut part of the shape
num_of_polygons = 100;
seed_num = 5;
Y = getPartialShape(X, num_of_polygons, seed_num);

%% show obj
figure();
subplot(2,1, 1);
patch('Faces',X.TRIV,'Vertices',X.VERT, 'FaceColor', 'blue');
subplot(2,1, 2);
patch('Faces',X.TRIV,'Vertices',X.VERT, 'FaceColor', 'blue');

%%