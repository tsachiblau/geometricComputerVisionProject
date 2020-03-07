close all;
clc; clear;
addpath('laplacian\');
%% load data
file_path = './dataset/shrec/null/dog.off';
X = load_off(file_path);
[laplace_X.W, ~, laplace_X.A] = calc_LB_FEM_bc(X, 'dirichlet');
[LBO_X.W, ~, LBO_X.A, LBO_X.Q] = calc_LBO_FEM_bc(X, 'dirichlet');


%% cut part of the shape

file_path = './dataset/shrec/cuts/cuts_dog_shape_1.off';
Y = load_off(file_path);
[laplace_Y.W, ~, laplace_Y.A] = calc_LB_FEM_bc(Y, 'dirichlet');
[LBO_Y.W, ~, LBO_Y.A, LBO_Y.Q] = calc_LBO_FEM_bc(Y, 'dirichlet');

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

%clac LBO
[LBO_X.eigenvectors, LBO_X.eigenvalue] = eigs(LBO_X.W, LBO_X.Q, number_of_eig, 'SM');
[LBO_Y.eigenvectors, LBO_Y.eigenvalue] = eigs(LBO_Y.W, LBO_Y.Q, number_of_eig, 'SM');

% %% look at the features
% 
% L = inv(laplace_X.A) * laplace_X.W;
% features = L * laplace_X.eigenvectors;
% features(isnan(features)) = 0;
% 
% L2 = inv(LBO_X.A) * LBO_X.W;
% features2 = L2 * LBO_X.eigenvectors;
% features2(isnan(features2)) = 0;
% 
% feature_reduction = tsne(features);
% feature_reduction_full = tsne([features, features2]);
% 
% figure();
% subplot(1,2,1);
% scatter(feature_reduction(:, 1), feature_reduction(:, 2));
% hold on;
% scatter(feature_reduction(Y.ORIGINAL_TRIV(:), 1), feature_reduction(Y.ORIGINAL_TRIV(:), 2), 'r');
% title('first laplacian');
% 
% subplot(1,2,2);
% scatter(feature_reduction_full(:, 1), feature_reduction_full(:, 2));
% hold on;
% scatter(feature_reduction_full(Y.ORIGINAL_TRIV(:), 1), feature_reduction_full(Y.ORIGINAL_TRIV(:), 2), 'r');
% title('two laplacians');
% 
% 
% y = zeros(3400, 1);
% y(Y.ORIGINAL_TRIV(:)) = 1;
% XXX = [features, y];
% XXX_e = [features, features2, y];

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
draw_th = 0.1;
eigenvalue_error_th = 1e-10;
tau = 10 * laplace_Y.eigenvalue(end);
% v = ones(size(X.VERT, 1), 1) * tau * 100;
v_oracle = getOracleV(X, Y);
v = v_oracle;
rng(5);
v(rand(size(v, 1), 1) < 0.1) = 1;

% v(sort(unique(Y.ORIGINAL_TRIV(:)))) = 0;
alpha = 1e-2;
mu = diag(laplace_Y.eigenvalue);
mu_LBO = diag(LBO_Y.eigenvalue);

iter = 1;
error_list = [];
error_list_LBO = [];
alpha_list = [];

f = figure();

while eigenvalue_error > eigenvalue_error_th
   
    %gradient of the smooth part
    [v_update, eigenvalue] = updateV(v, laplace_X.W, laplace_X.A, mu, number_of_eig, alpha);
    [v_update_LBO, eigenvalue_LBO] = updateV(v, LBO_X.W, LBO_X.Q, mu_LBO, number_of_eig, alpha);

%     v = max(v - v_update - v_update_LBO, 0);

    v = max(v - v_update, 0);
    
    eigenvalue_error = norm(diag(eigenvalue) - mu);
    eigenvalue_error_LBO = norm(diag(eigenvalue_LBO) - mu_LBO);

    error_list = [error_list, eigenvalue_error];
    error_list_LBO = [error_list_LBO, eigenvalue_error_LBO];
    alpha_list = [alpha_list, alpha];
    
    if mod(iter, 5) == 0 & iter > 10
        clf(f);
        
        subplot(2, 4, 1);
        plot(1:size(error_list, 2), error_list);
        title('eigenvalue norm error LB');
        
        subplot(2, 4, 2);
        plot(1:size(error_list_LBO, 2), error_list_LBO);
        title('eigenvalue norm error LBO');
        
        subplot(2, 4, 3);
        scatter(1:size(v, 1), v);
        idx_to_draw = v < draw_th;
        subplot(2, 4, 4);
        patch('Faces',X.TRIV,'Vertices',X.VERT, 'FaceColor', 'blue');
        hold on;
        patch('Faces',Y.TRIV,'Vertices',Y.VERT, 'FaceColor', 'green');
        hold on;
        scatter3(X.VERT(idx_to_draw,1), X.VERT(idx_to_draw,2), X.VERT(idx_to_draw,3), 'r', 'filled');
        title({['in the shape: ', num2str(sum(idx_to_draw & (v_oracle < draw_th))), '/', num2str(Y.n)],...
                ['not in shape: ', num2str(sum(idx_to_draw & (v_oracle > draw_th)))]});
        
        subplot(2, 4, 5);
        plot( 1 : size(diag(eigenvalue), 1), diag(eigenvalue), 'r');
        hold on;
        plot( 1 : size(laplace_Y.eigenvalue, 2), diag(laplace_Y.eigenvalue), 'b');
        legend('X', 'Y');
        title('eigenvalue of LB');
        
        subplot(2, 4, 6);
        plot( 1 : size(diag(eigenvalue_LBO), 1), diag(eigenvalue_LBO), 'r');
        hold on;
        plot( 1 : size(LBO_Y.eigenvalue, 2), diag(LBO_Y.eigenvalue), 'b');
        legend('X', 'Y');
        title('eigenvalue of LBO');       
        subplot(2, 4, 7);
        plot( 1 : size(alpha_list, 2), alpha_list);
        pause(0.001);
        
        alpha = updateAlpha(error_list, alpha);

    end
    
    iter = iter + 1;
end












