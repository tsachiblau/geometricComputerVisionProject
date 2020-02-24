function [grad_v, eigenvalue] = updateV(v, laplace_X, mu, number_of_eig, alpha)
    
    ex1 = sparse(laplace_X.W + laplace_X.A * diag(v));
    [eigenvectors, eigenvalue] = eigs(ex1 , laplace_X.A, number_of_eig, 'SM');
    ex2 = eigenvectors .* eigenvectors;
    ex3 = (diag(eigenvalue) - mu) ./ (mu .^ 2);
    ex4 = 2 * alpha * ex2 * ex3;
    grad_v = max(ex4, 0);
end

