function [grad_v, eigenvalue] = updateV(v, W, A, mu, number_of_eig, alpha)
    
    ex1 = sparse(W + A * diag(v));
        [eigenvectors, eigenvalue] = eigs(ex1 , A, number_of_eig, 'SM');
    ex2 = eigenvectors .* eigenvectors;
    ex3 = (diag(eigenvalue) - mu) ./ (mu .^ 2);
    ex4 = 2 * alpha * ex2 * ex3;
    grad_v = ex4;
end

