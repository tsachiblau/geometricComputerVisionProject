close all;
clc; clear;
addpath('laplacian\');
%% load data
file_path = './dataset/dog0';
X = load_off(file_path);
[laplace_X.W, ~, laplace_X.A] = calc_LB_FEM_bc(X, 'dirichlet');

%% cut part of the shape
num_of_polygons = 100;
seed = 1;
Y = getPartialShape(X, num_of_polygons, seed);
[laplace_Y.W, ~, laplace_Y.A] = calc_LB_FEM_bc(Y, 'dirichlet');

%% show obj
figure();
patch('Faces',X.TRIV,'Vertices',X.VERT, 'FaceColor', 'blue');
hold on;
patch('Faces',Y.TRIV,'Vertices',Y.VERT, 'FaceColor', 'green');
title('show patch');
%% show eignevectors

number_of_eig = 20;
[laplace_X.eigenvectors, laplace_X.eigenvalue] = eigs(laplace_X.W, laplace_X.A, number_of_eig, 'SM');
[~, laplace_Y.eigenvalue] = eigs(laplace_Y.W, laplace_Y.A, number_of_eig , 'SM');
%%
figure();
i = 1;
for row = 1 : 2
    for col = 1 : 10
        subplot(2, 10, i);
        patch('Faces',X.TRIV,'Vertices',X.VERT, 'FaceVertexCData',laplace_X.eigenvectors(:,i),'FaceColor','flat');
        title(['eigenvalue number', num2str(i) ,'   is', num2str(laplace_X.eigenvalue(i, i))]);
        i = i + 1;
    end 
end

%% show eigenvalue graph