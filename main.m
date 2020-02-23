close all;
clc; clear;
addpath('laplacian\');
%% load data
file_path = './dataset/dog0';
X = load_off(file_path);
[laplace_X.W, ~, laplace_X.A] = calc_LB_FEM_bc(X, 'dirichlet');


%% cut part of the shape


num_of_polygons = 1000;
seed = 503;
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
[laplace_Y.eigenvectors, laplace_Y.eigenvalue] = eigs(laplace_Y.W, laplace_Y.A, number_of_eig, 'SM');
%% show eigenvalue on complete shape
figure();
i = 1;
for row = 1 : 2
    for col = 1 : 10
        subplot(2, 10, i);
        patch('Faces',X.TRIV,'Vertices',X.VERT, 'FaceVertexCData',laplace_X.eigenvectors(:,i),'EdgeAlpha', 0, 'FaceColor', 'interp');
        title(['eigenvalue number', num2str(i) ,'   is', num2str(laplace_X.eigenvalue(i, i))]);
        i = i + 1;
    end 
end

%% show eigenvalue on complete shape
figure();
i = 1;
for row = 1 : 2
    for col = 1 : 10
        subplot(2, 10, i);
        patch('Faces',Y.TRIV,'Vertices',Y.VERT, 'FaceVertexCData',laplace_Y.eigenvectors(:,i),'EdgeAlpha', 0, 'FaceColor', 'interp');
        title(['eigenvalue number', num2str(i) ,'   is', num2str(laplace_Y.eigenvalue(i, i))]);
        i = i + 1;
    end 
end


%% show eigenvalue graph
figure();
plot( 1 : size(laplace_X.eigenvalue, 2), diag(laplace_X.eigenvalue), 'r');
hold on;
plot( 1 : size(laplace_Y.eigenvalue, 2), diag(laplace_Y.eigenvalue), 'b');
legend('X', 'Y');

%% optimization 
eigenvalue_error = 2;
draw_th = 1e-3;
eigenvalue_error_th = 1e-3;
tau = 10 * laplace_Y.eigenvalue(end);
v = ones(size(X.VERT, 1), 1) * tau * 100;
% v(sort(unique(Y.ORIGINAL_TRIV(:)))) = 0;
alpha = 1e-4;
mu = diag(laplace_Y.eigenvalue);
iter = 1;
error_list = [];

f = figure();

while eigenvalue_error > eigenvalue_error_th
    ex1 = sparse(laplace_X.W + laplace_X.A * diag(v));
    [eigenvectors, eigenvalue] = eigs(ex1 , laplace_X.A, number_of_eig, 'SM');
    ex2 = eigenvectors .* eigenvectors;
    ex3 = (diag(eigenvalue) - mu) ./ (mu .^ 2);
    ex4 = 2 * alpha * ex2 * ex3;
    
    %gradient of the smooth part
    ex5 = getVectorSmoother(v, X, alpha);
    v = v - max(ex4, 0) -  ex5;
    
    eigenvalue_error = norm(diag(eigenvalue) - mu);
    error_list = [error_list, eigenvalue_error];
    
    if mod(iter, 100) == 0
        clf(f);
        subplot(2, 2, 1);
        plot(1:size(error_list, 2), error_list);
        title('eigenvalue norm error');
        subplot(2, 2, 3);
        scatter(1:size(v, 1), v);
        
        idx_to_draw = v < draw_th;
        subplot(2, 2, 2);

        patch('Faces',X.TRIV,'Vertices',X.VERT, 'FaceColor', 'blue');
        hold on;
        patch('Faces',Y.TRIV,'Vertices',Y.VERT, 'FaceColor', 'green');
        hold on;
        scatter3(X.VERT(idx_to_draw,1), X.VERT(idx_to_draw,2), X.VERT(idx_to_draw,3), 'r', 'filled');
        title('show patch');
        subplot(2, 2, 4);
        plot( 1 : size(diag(eigenvalue), 1), diag(eigenvalue), 'r');
        hold on;
        plot( 1 : size(laplace_Y.eigenvalue, 2), diag(laplace_Y.eigenvalue), 'b');
        legend('X', 'Y');
        pause(0.001);
    end
    
    iter = iter + 1;
end












