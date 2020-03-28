close all;
clc; clear;
addpath('laplacian\');
rng(5);

%% load data
shape_name = 'dog';
% shape_name = 'centaur';
file_path = ['./dataset/shrec/null/', shape_name, '.off'];
X = load_off(file_path);
[laplace_X.W, ~, laplace_X.A] = calc_LB_FEM_bc(X, 'dirichlet');
[LBO_X.W, ~, LBO_X.A, LBO_X.Q] = calc_LBO_FEM_bc(X, 'dirichlet');

%% cut part of the shape
file_path = ['./dataset/shrec/cuts/cuts_', shape_name, '_shape_1.off'];
Y = load_off(file_path);
[laplace_Y.W, ~, laplace_Y.A] = calc_LB_FEM_bc(Y, 'dirichlet');
[LBO_Y.W, ~, LBO_Y.A, LBO_Y.Q] = calc_LBO_FEM_bc(Y, 'dirichlet');

%% show obj
figure();
patch('Faces',X.TRIV,'Vertices',X.VERT, 'FaceColor', 'blue', 'edgecolor', 'none');
hold on;
patch('Faces',Y.TRIV,'Vertices',Y.VERT, 'FaceColor', 'green', 'edgecolor', 'none');
title('show patch');

%% show eignevectors
number_of_eig = 20;
[laplace_X.eigenvectors, laplace_X.eigenvalue] = eigs(laplace_X.W, laplace_X.A, number_of_eig, 'SM');
[laplace_Y.eigenvectors, laplace_Y.eigenvalue] = eigs(laplace_Y.W, laplace_Y.A, number_of_eig, 'SM');

%clac LBO
[LBO_X.eigenvectors, LBO_X.eigenvalue] = eigs(LBO_X.W, LBO_X.Q, number_of_eig, 'SM');
[LBO_Y.eigenvectors, LBO_Y.eigenvalue] = eigs(LBO_Y.W, LBO_Y.Q, number_of_eig, 'SM');

%% show eigenvalue on complete shape
figure();
i = 1;
for row = 1 : 2
    for col = 1 : 10
        subplot(2, 10, i);
        patch('Faces',X.TRIV,'Vertices',X.VERT, 'FaceVertexCData',laplace_X.eigenvectors(:,i),'EdgeAlpha', 0, 'FaceColor', 'interp');
        title(['eig #', num2str(i) ,': ', num2str(laplace_X.eigenvalue(i, i))]);
        i = i + 1;
    end 
end

%% show eigenvalue on partial shape
figure();
i = 1;
for row = 1 : 2
    for col = 1 : 10
        subplot(2, 10, i);
        
        patch('Faces',X.TRIV,'Vertices',X.VERT, 'FaceVertexCData',laplace_X.eigenvectors(:,i),'EdgeAlpha', 0, 'FaceColor', 'none');
        patch('Faces',Y.TRIV,'Vertices',Y.VERT, 'FaceVertexCData',laplace_Y.eigenvectors(:,i),'EdgeAlpha', 0, 'FaceColor', 'interp');
        title(['eig #', num2str(i) ,': ', num2str(laplace_X.eigenvalue(i, i))]);
        i = i + 1;
    end 
end

%% show eigenvalues of the partial and of the whole shape on a graph
figure();
plot( 1 : size(laplace_X.eigenvalue, 2), diag(laplace_X.eigenvalue), 'r');
hold on;
plot( 1 : size(laplace_Y.eigenvalue, 2), diag(laplace_Y.eigenvalue), 'b');
legend('X', 'Y');

%% optimization 

%set constants 
eigenvalue_error = 2;
eigenvalue_error_th = 1e-10;
tau = 10 * laplace_Y.eigenvalue(end);
draw_th = tau / 100;
min_error = 100;

%get the oracle V
v_oracle = getOracleV(X, Y);

%get a group of not correlated, random v inititilizations
random_v = getRandomV(X)';

%this loop go over all the v random different initilizations
for i = 1 : size(random_v, 2)
    v = random_v(:, i) * tau * 100;
%     v = v_oracle * tau * 100;
    
    %prepare for the inner loop
    mu = diag(laplace_Y.eigenvalue);
    mu_LBO = diag(LBO_Y.eigenvalue);
    alpha = 1e-4;
    iter = 1;
    error_list = [];
    error_list_LBO = [];
    alpha_list = [];
    TP_list = [];
    f = figure();
    v_initial = v;
    
    while eigenvalue_error > eigenvalue_error_th & iter < 300000

        %gradient of the smooth part
        [v_update, eigenvalue] = updateV(v, laplace_X.W, laplace_X.A, mu, number_of_eig, alpha);
        [v_update_LBO, eigenvalue_LBO] = updateV(v, LBO_X.W, LBO_X.Q, mu_LBO, number_of_eig, alpha);

        %keep v in the domain
        v = max(v - v_update - v_update_LBO, 0);
        v = min(v, tau * 100);

        eigenvalue_error = norm(diag(eigenvalue) - mu);
        eigenvalue_error_LBO = norm(diag(eigenvalue_LBO) - mu_LBO);

        %update list for graphs
        error_list = [error_list, eigenvalue_error];
        error_list_LBO = [error_list_LBO, eigenvalue_error_LBO];
        alpha_list = [alpha_list, alpha];
        TP_list = [TP_list, sum((v < draw_th) & (v_oracle < draw_th))];
        
        if mod(iter, 5) == 0 & iter > 10
            clf(f);

            subplot(2, 4, 1);
            plot(1:size(error_list, 2), error_list);
            title('eigenvalue norm error LB');

            subplot(2, 4, 2);
            plot(1:size(error_list_LBO, 2), error_list_LBO);
            title('eigenvalue norm error LBO');

            subplot(2, 4, 3);
            scatter(1:size(v, 1), v, 'b');
            hold on;
            scatter(1:size(v, 1), v_initial, 'r');
            idx_to_draw = v < draw_th;
            title('value of v');

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

            subplot(2, 4, 8);
            plot( 1 : size(TP_list, 2), TP_list, 'b');
            hold on;
            plot( 1 : size(TP_list, 2), ones(size(TP_list, 2),1) * Y.n, 'r');       
            title('number of TP');

            pause(0.001);
            alpha = updateAlpha(error_list, alpha);
        end

        iter = iter + 1;
    end

    if eigenvalue_error < min_error
        min_error = eigenvalue_error
        best_v = v;
    end
end

%plot the best result
figure();
idx_to_draw = best_v < draw_th;
patch('Faces',X.TRIV,'Vertices',X.VERT, 'FaceColor', 'blue');
hold on;
patch('Faces',Y.TRIV,'Vertices',Y.VERT, 'FaceColor', 'green');
hold on;
scatter3(X.VERT(idx_to_draw,1), X.VERT(idx_to_draw,2), X.VERT(idx_to_draw,3), 'r', 'filled');